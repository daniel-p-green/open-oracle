import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from evidence import AdmissionHeld,TrialLedger,build_bundle,paid_agents_preflight

class EvidenceAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        original=b'public official fixture original';extract='Candidate identity H4MO05234.'
        (self.root/'source.bin').write_bytes(original);(self.root/'text.txt').write_text(extract)
        source={'id':'filing','url':'https://docquery.fec.gov/pdf/fixture.pdf','retrieved_url':'https://docquery.fec.gov/pdf/fixture.pdf','publisher':'FEC','document_date':'2026-06-21','retrieved_utc':'2026-10-24T00:00:00+00:00','candidate_fec_id':'H4MO05234','source_class':'official_candidate_filing','claim_role':'filed_assertion','admission':'limited_local_review','rights':{'public_reuse':False},'original_file':'source.bin','extraction_file':'text.txt','original_sha256':hashlib.sha256(original).hexdigest(),'extraction_sha256':hashlib.sha256(extract.encode()).hexdigest(),'passages':[{'id':'id','quote':'H4MO05234','start':19,'end':28,'locator':'page 1'}]}
        self.registry={'candidate':{'fec_id':'H4MO05234'},'sources':[source],'coverage_gaps':['debate_unavailable'],'identity_review':'fixture_only'}
    def tearDown(self):self.temp.cleanup()
    def test_exact_original_version_span_and_role_form_an_offline_nonpublic_bundle(self):
        bundle=build_bundle(self.registry,self.root);self.assertFalse(bundle['publication_enabled']);self.assertFalse(bundle['model_inference']);self.assertEqual(bundle['personal_ballot_membership'],'unknown');self.assertEqual(bundle['evidence'][0]['role'],'filed_assertion')
    def test_newsroom_source_foreign_candidate_and_promotion_of_claim_to_fact_rejected(self):
        for field,value in [('source_class','journalism'),('candidate_fec_id','H0MO00000'),('claim_role','established_fact'),('url','https://attacker.invalid/x')]:
            r=copy.deepcopy(self.registry);r['sources'][0][field]=value
            with self.assertRaises(AdmissionHeld):build_bundle(r,self.root)
    def test_hash_change_forged_span_missing_rights_and_path_escape_rejected(self):
        for field,value in [('original_sha256','0'*64),('passages',[{'id':'id','quote':'Vote Yes','start':0,'end':8,'locator':'page 1'}]),('rights',{'public_reuse':True}),('original_file','../secret')]:
            r=copy.deepcopy(self.registry);r['sources'][0][field]=value
            with self.assertRaises(AdmissionHeld):build_bundle(r,self.root)

class TrialLedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/'effects.sqlite';self.ledger=TrialLedger(self.path)
    def tearDown(self):self.ledger.close();self.temp.cleanup()
    def test_retry_reuses_submission_identity_across_reopen_and_cannot_dispatch_twice(self):
        first=self.ledger.prepare('job','bundle');self.assertTrue(self.ledger.begin_submission('job'));self.ledger.close();self.ledger=TrialLedger(self.path)
        self.assertEqual(self.ledger.prepare('job','bundle')['submission_key'],first['submission_key']);self.assertFalse(self.ledger.begin_submission('job'))
        with self.assertRaises(AdmissionHeld):self.ledger.prepare('job','changed_bundle')
    def test_stop_before_submission_prevents_dispatch(self):
        self.ledger.prepare('job','bundle');self.assertEqual(self.ledger.stop('job'),'cancelled_locally');self.assertFalse(self.ledger.begin_submission('job'))
    def test_unknown_creation_outcome_stays_uncertain_and_never_retries(self):
        self.ledger.prepare('job','bundle');self.ledger.begin_submission('job');self.assertEqual(self.ledger.stop('job'),'uncertain_remote');self.assertFalse(self.ledger.begin_submission('job'))
        with self.assertRaises(AdmissionHeld):self.ledger.acknowledge_cancel('job')
        submission=self.ledger.prepare('job','bundle')['submission_key']
        self.assertEqual(self.ledger.submitted('job',submission,'late_known_session'),'stop_requested')
        self.assertFalse(self.ledger.begin_submission('job'));self.ledger.acknowledge_cancel('job')
    def test_cancel_request_is_not_confirmation_and_late_submission_is_rejected(self):
        submission=self.ledger.prepare('job','bundle')['submission_key'];self.ledger.begin_submission('job');self.ledger.submitted('job',submission,'test_session');self.assertEqual(self.ledger.stop('job'),'stop_requested');self.ledger.acknowledge_cancel('job');self.assertEqual(self.ledger.stop('job'),'cancelled_confirmed');self.assertFalse(self.ledger.begin_submission('job'))
        self.assertEqual(self.ledger.submitted('job',submission,'test_session'),'cancelled_confirmed')
        with self.assertRaises(AdmissionHeld):self.ledger.submitted('job',submission,'different_session')
