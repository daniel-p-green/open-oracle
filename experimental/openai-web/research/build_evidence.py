"""Compile one local-only primary evidence bundle; never invokes a model."""
import argparse
from datetime import datetime,timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
from evidence import build_bundle,TrialLedger,paid_agents_preflight,AdmissionHeld

REPOSITORY=Path(__file__).resolve().parents[3]
PINS={
 'fec-candidacy.pdf':('82c0b49b0949eb68229583316b4e0dc05c7cf6a46162e758f52dfa6fb1c0177c','https://docquery.fec.gov/pdf/614/202606219874229614/202606219874229614.pdf'),
 'campaign-issues.html':('b2ef1c53c97702ee994eb13e3c8c09d59194167ea05b2992c1a5f4acb9860a69','https://www.cleaver4congress.com/issues'),
 'campaign-about.html':('fb488badf1c3779d6cea11869d1b3aa758ba3f11a31aede785bf546e731a5fc0','https://www.cleaver4congress.com/about')}
class PlainText(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.parts=[];self.block=0
 def handle_starttag(self,tag,attrs):
  if tag in {'script','style','noscript','template'}:self.block+=1
 def handle_endtag(self,tag):
  if tag in {'script','style','noscript','template'}:self.block=max(0,self.block-1)
 def handle_data(self,value):
  if not self.block and value.strip():self.parts.append(value.strip())

def compile_evidence(inputs,output):
 inputs=Path(inputs).resolve();output=Path(output).resolve()
 if inputs.is_relative_to(REPOSITORY) or output.is_relative_to(REPOSITORY):raise AdmissionHeld('private_artifact_location')
 manifest=json.loads((inputs/'manifest.json').read_text());sources=[]
 for name,(pin,url) in PINS.items():
  row=next(r for r in manifest if r['name']==name)
  original=(inputs/name).read_bytes()
  if hashlib.sha256(original).hexdigest()!=pin or row['sha256']!=pin or row['url']!=url or row['final_url']!=url:raise AdmissionHeld('unadmitted_version')
  if name.endswith('.pdf'):
   # No shell, no OCR guess. Keep raw extraction private and select only safe fields.
   text=subprocess.run(['pdftotext','-layout',str(inputs/name),'-'],capture_output=True,check=True,timeout=10).stdout.decode()
   quote='H4MO05234';kind='official_candidate_filing';role='filed_assertion';sid='fec-form2';locator='PDF page 1, candidate identification field';date='2026-06-21'
   if 'Cleaver II, Emanuel' not in text or 'CLEAVER FOR CONGRESS' not in text or '2026' not in text:raise AdmissionHeld('filing_identity')
   extractor='pdftotext -layout; exact page-one field; no OCR'
  else:
   parser=PlainText();parser.feed(original.decode());text='\n'.join(parser.parts)+'\n';date=None;extractor='stdlib HTMLParser, script/style/noscript/template excluded; newline-joined text nodes v1'
   if name=='campaign-issues.html':
    quote='He believes the ACA should be strengthened.';kind='official_campaign_statement';role='attributed_campaign_claim';sid='campaign-aca';locator='Health Care section; exact extraction code-point span'
   else:
    quote='Emanuel Cleaver, II';kind='campaign_identity';role='campaign_self_identification';sid='campaign-identity';locator='About section; exact extraction code-point span'
   if 'Cleaver for Congress' not in text:raise AdmissionHeld('publisher_identity')
  extraction=name+'.extracted.txt';(inputs/extraction).write_text(text)
  start=text.index(quote)
  sources.append({'id':sid,'source_class':kind,'claim_role':role,'admission':'limited_local_review','candidate_fec_id':'H4MO05234',
    'url':url,'retrieved_url':row['final_url'],'publisher':'Federal Election Commission' if kind=='official_candidate_filing' else 'Cleaver for Congress (campaign)',
    'document_date':date,'retrieved_utc':row['retrieved_utc'],'original_file':name,'original_sha256':pin,
    'extraction_file':extraction,'extraction_sha256':hashlib.sha256(text.encode()).hexdigest(),'extractor':extractor,
    'rights':{'scope':'factual filing identifier / short attributed campaign excerpt for local review only','public_reuse':False,'license':'not_established','model_use':'held_pending_trial_controls'},
    'passages':[{'id':sid+'-p1','quote':quote,'start':start,'end':start+len(quote),'locator':locator}]})
 registry={'candidate':{'fec_id':'H4MO05234','name':'Emanuel Cleaver, II','office':'US House','state':'MO','district':'05','filing_election_year':2026,'committee_id':'C00395848','scope':'federal filing and attributed campaign material; not official personal ballot membership'},
   'sources':sources,
   'identity_review':{'kind':'agent_limited_local_review','basis':'Form2 candidate ID/full name, election year, office and named principal committee; campaign full-name/district/self-identification and matching public campaign contact. Not a name-only merge.','human_approval':'pending','publication':'held'},
   'coverage_gaps':[{'class':'original_debate_transcript','state':'missing','reason':'No rights-cleared original transcript supplied/admitted; no captions downloaded.'},
                    {'class':'missouri_ballot_certification','state':'unavailable','reason':'Both direct SOS original downloads returned HTTP403; no retry or alternate retrieval. Federal filing does not establish ballot membership.'}]}
 output.mkdir(parents=True,exist_ok=True)
 bundle=build_bundle(registry,inputs)
 (output/'registry.json').write_text(json.dumps(registry,indent=2)+'\n');(output/'bundle.json').write_text(json.dumps(bundle,indent=2)+'\n')
 ledger=TrialLedger(output/'effects.sqlite')
 key='candidate-primary-bundle-v1';first=ledger.prepare(key,bundle['bundle_sha256']);second=ledger.prepare(key,bundle['bundle_sha256'])
 try:paid_agents_preflight()
 except AdmissionHeld as error:blocked=str(error)
 state=ledger.stop(key);ledger.close()
 receipt={'completed_utc':datetime.now(timezone.utc).isoformat(),'kind':'offline_primary_source_bundle','bundle_sha256':bundle['bundle_sha256'],
   'sources_retained':len(sources),'original_and_extraction_hashes_verified':True,'exact_passages':len(sources),
   'source_classes':[s['source_class'] for s in sources],'idempotent_local_prepare':first['submission_key']==second['submission_key'],
   'local_state':state,'paid_trial_state':'blocked_before_session_create','blocker':blocked,'provider_requests':0,'new_spend_usd':0,'new_reservation_usd':0,
   'requested_trial_reservation_ceiling_usd':5,'publication_enabled':False,'human_review':'pending','coverage_gaps':registry['coverage_gaps']}
 (output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2));return receipt

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--inputs',required=True,type=Path);parser.add_argument('--output',required=True,type=Path);args=parser.parse_args();compile_evidence(args.inputs,args.output)
