"""Offline primary-source admission and an effects ledger; paid Agents dispatch is held."""
import copy
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import uuid

class AdmissionHeld(ValueError):pass


def digest(data):return hashlib.sha256(data).hexdigest()


def build_bundle(registry, originals):
    """Registry is application-owned admission configuration, never a model result."""
    registry=copy.deepcopy(registry);root=Path(originals).resolve();evidence=[]
    candidate=registry['candidate']
    if not re.fullmatch(r'H[0-9A-Z]{8}',candidate['fec_id']):raise AdmissionHeld('candidate_identity')
    for source in registry['sources']:
        if source['source_class'] not in {'official_candidate_filing','official_campaign_statement','campaign_identity'}:raise AdmissionHeld('bad_source_class')
        if source['admission']!='limited_local_review' or source['rights']['public_reuse'] is not False:raise AdmissionHeld('rights_scope')
        if source['candidate_fec_id']!=candidate['fec_id']:raise AdmissionHeld('candidate_mismatch')
        roles={'official_candidate_filing':'filed_assertion','official_campaign_statement':'attributed_campaign_claim','campaign_identity':'campaign_self_identification'}
        if source['claim_role']!=roles[source['source_class']]:raise AdmissionHeld('claim_role')
        expected_host='https://docquery.fec.gov/pdf/' if source['source_class']=='official_candidate_filing' else 'https://www.cleaver4congress.com/'
        if not source['url'].startswith(expected_host) or source['url']!=source['retrieved_url']:raise AdmissionHeld('publisher_scope')
        try:
            timestamp=datetime.fromisoformat(source['retrieved_utc'])
            if timestamp.tzinfo is None:raise ValueError()
        except Exception:raise AdmissionHeld('retrieval_timestamp') from None
        objects=[]
        for name,expected in [(source['original_file'],source['original_sha256']),(source['extraction_file'],source['extraction_sha256'])]:
            path=(root/name).resolve()
            if path.parent!=root or not path.is_file() or path.stat().st_size>4*1024*1024:raise AdmissionHeld('object_path_or_bound')
            raw=path.read_bytes()
            if digest(raw)!=expected:raise AdmissionHeld('version_integrity')
            objects.append(raw)
        text=objects[1].decode('utf-8')
        passages=[]
        for passage in source['passages']:
            start,end=passage['start'],passage['end']
            if type(start) is not int or type(end) is not int or not 0<=start<end<=len(text) or text[start:end]!=passage['quote']:raise AdmissionHeld('citation_span')
            if len(passage['quote'])>240:raise AdmissionHeld('excerpt_bound')
            passages.append({'id':passage['id'],'quote':passage['quote'],'start':start,'end':end,'locator':passage['locator']})
        evidence.append({'source_id':source['id'],'class':source['source_class'],'role':source['claim_role'],
                         'original_sha256':source['original_sha256'],'extraction_sha256':source['extraction_sha256'],
                         'url':source['url'],'publisher':source['publisher'],'document_date':source['document_date'],
                         'retrieved_utc':source['retrieved_utc'],'candidate_fec_id':source['candidate_fec_id'],
                         'passages':passages,'rights':source['rights']})
    if len({s['id'] for s in registry['sources']})!=len(evidence):raise AdmissionHeld('duplicate_source')
    bundle={'schema_version':1,'candidate':candidate,'evidence':evidence,'coverage_gaps':registry['coverage_gaps'],
            'personal_ballot_membership':'unknown','publication_enabled':False,'model_inference':False,
            'identity_review':registry['identity_review']}
    bundle['bundle_sha256']=digest(json.dumps(bundle,sort_keys=True,separators=(',',':')).encode())
    return bundle


def paid_agents_preflight():
    # No runtime override. Local timers/stream closure cannot cap an asynchronous
    # remote turn when create outcome/session ID or cancel acknowledgement is lost.
    # No documented per-run hard cost/token cap was verified in the inspected schema.
    raise AdmissionHeld('agents_remote_cost_and_hard_stop_unverified')


class TrialLedger:
    """Durable logical-job idempotence. No network or inference capability."""
    def __init__(self,path):
        self.db=sqlite3.connect(path)
        self.db.execute('CREATE TABLE IF NOT EXISTS jobs (key TEXT PRIMARY KEY, bundle TEXT NOT NULL, submission_key TEXT NOT NULL, state TEXT NOT NULL, session TEXT)')
        self.db.commit()
    def prepare(self,key,bundle):
        with self.db:
            self.db.execute('INSERT OR IGNORE INTO jobs VALUES (?,?,?,?,NULL)',(key,bundle,str(uuid.uuid4()),'prepared'))
            row=self.db.execute('SELECT bundle,submission_key,state FROM jobs WHERE key=?',(key,)).fetchone()
            if row[0]!=bundle:raise AdmissionHeld('idempotence_conflict')
        return {'bundle':row[0],'submission_key':row[1],'state':row[2]}
    def begin_submission(self,key):
        # A production dispatcher must also pass paid_agents_preflight first.
        with self.db:
            cursor=self.db.execute("UPDATE jobs SET state='dispatching' WHERE key=? AND state='prepared'",(key,))
        return cursor.rowcount==1
    def submitted(self,key,submission_key,session):
        if not isinstance(session,str) or not 1<=len(session)<=256:raise AdmissionHeld('session_identity')
        with self.db:
            row=self.db.execute('SELECT submission_key,state,session FROM jobs WHERE key=?',(key,)).fetchone()
            if not row or row[0]!=submission_key:raise AdmissionHeld('stale_submission')
            _,state,known=row
            if known:
                if known!=session:raise AdmissionHeld('session_conflict')
                return state  # Duplicate acknowledgement never resumes stopped work.
            if state not in {'dispatching','uncertain_remote'}:raise AdmissionHeld('stale_submission')
            new='submitted' if state=='dispatching' else 'stop_requested'
            self.db.execute('UPDATE jobs SET state=?,session=? WHERE key=?',(new,session,key))
            return new
    def stop(self,key):
        with self.db:
            row=self.db.execute('SELECT state,session FROM jobs WHERE key=?',(key,)).fetchone()
            if not row:raise AdmissionHeld('unknown_job')
            state,session=row
            if state in {'prepared','dispatching','submitted'}:
                new='cancelled_locally' if state=='prepared' else ('stop_requested' if session else 'uncertain_remote')
                self.db.execute('UPDATE jobs SET state=? WHERE key=?',(new,key))
                return new
        return state
    def acknowledge_cancel(self,key):
        with self.db:
            changed=self.db.execute("UPDATE jobs SET state='cancelled_confirmed' WHERE key=? AND state='stop_requested'",(key,)).rowcount
        if not changed:raise AdmissionHeld('cancel_unconfirmed')
    def close(self):self.db.close()
