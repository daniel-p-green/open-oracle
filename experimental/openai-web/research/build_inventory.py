"""Reconcile pinned official public notices; no model, network or personal ballot.

Retained originals are read only. Explicit contest/party crosswalks organize
source rows, never merge person identities or infer residential applicability.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

KPIN='92cda731c864b5a84062322a32f743597bcace6f986af4c0e2bfe55c7405dc62'
JPIN='032814e650dbdbdb0064acb396ead6f51dcd087778240802eb6c30c7a5ef64a2'
# Reviewed against the rendered notices. Candidate strings are search anchors;
# emitted spelling/case/punctuation always comes from the source text layer.
CANDIDATES=[
 ('auditor','State Auditor',1,'SCOTT FITZPATRICK|REP;QUENTIN WILSON|DEM;DUSTIN COFFELL|LIB'),
 ('us-house-4','U.S. House · District 4',1,'MARK ALFORD|REP;JORDAN HERRERA|DEM;THOMAS HOLBROOK|LIB'),
 ('us-house-5','U.S. House · District 5',1,'RICK BRATTIN|REP;EMANUEL CLEAVER, II|DEM;RANDALL (RANDY) LANGKRAEHR|LIB'),
 ('us-house-6','U.S. House · District 6',1,'CHRIS STIGALL|REP;JOSH SMEAD|DEM;ANDY MAIDMENT|LIB'),
 ('state-senate-8','State Senate · District 8',1,'JON PATTERSON|REP;KERI INGLE|DEM'),
 ('state-house-19','State House · District 19',1,'KAREN IRENE SPALDING|REP;WICK THOMAS|DEM'),
 ('state-house-20','State House · District 20',1,'MIKE STEINMEYER|REP;JEFF SPICER|DEM'),
 ('state-house-21','State House · District 21',1,'MICHAEL YOUNG|REP;WILL JOBE|DEM'),
 ('state-house-22','State House · District 22',1,'YOLANDA YOUNG|DEM'),
 ('state-house-28','State House · District 28',1,'STEVEN W. HINTON|REP;DONNA BARNES|DEM'),
 ('state-house-29','State House · District 29',1,'ROBERT BRUETTE|REP;TEDI H. ROWLAND|DEM'),
 ('state-house-30','State House · District 30',1,'JEFF MARTIN|REP;KEVIN GROVER|DEM'),
 ('state-house-31','State House · District 31',1,'RON FOWLER|REP;JUSTIN GEISER|DEM'),
 ('state-house-32','State House · District 32',1,'MICHAEL TODD|REP;JENNIFER CASSIDY|DEM'),
 ('state-house-33','State House · District 33',1,'CAROLYN CATON|REP;TROY LATTERELL|DEM'),
 ('state-house-34','State House · District 34',1,'SEAN SMITH|REP;KEMP STRICKLER|DEM'),
 ('state-house-35','State House · District 35',1,'JACQUIE AZIERE STENGER|REP;MICHAEL SCOTT|DEM'),
 ('state-house-36','State House · District 36',1,'DAVE THOMAS|REP;ANTHONY T. EALY, JR.|DEM'),
 ('county-executive','Jackson County Executive',2,'ALAN ROHLFING|REP;STACY LAKE|DEM'),
 ('county-at-large-1','County Legislature · At-large 1',2,'LANCE POLLARD|REP;CARLA FIELDS|DEM'),
 ('county-at-large-2','County Legislature · At-large 2',2,'GRESIA CABRERA|REP;DONNA PEYTON|DEM'),
 ('county-at-large-3','County Legislature · At-large 3',2,'SUSAN B. WILSON|DEM'),
 ('county-district-2','County Legislature · District 2',2,'VENESSA HUSKEY|DEM'),
 ('county-district-3','County Legislature · District 3',2,'SCOTT QUALLS|REP;PHYLLIS HERNANDEZ|DEM'),
 ('county-district-4','County Legislature · District 4',2,'LON MCDONALD|REP;BYRON TOWNSEND|DEM'),
 ('county-district-5','County Legislature · District 5',2,'DALE CARTER|REP;ANTOINE D. JENNINGS|DEM'),
 ('county-district-6','County Legislature · District 6',2,'BILL HALEY|REP;TONY LAWSON|DEM'),
 ('state-house-23','State House · District 23',0,'TONY L. VAN TRECE|DEM'),
 ('state-house-24','State House · District 24',0,'KEVIN GARNER|DEM'),
 ('state-house-25','State House · District 25',0,'PATTIE MANSUR|DEM'),
 ('state-house-26','State House · District 26',0,'TIFFANY PRICE|DEM'),
 ('state-house-27','State House · District 27',0,'MELISSA A DOUGLAS|DEM'),
 ('state-house-37','State House · District 37',0,'KARISSA MARIE VARGA|DEM'),
 ('county-district-1','County Legislature · District 1',0,'KELLY THOMPSON|DEM'),
]
K_PAGES={
 'auditor':2,'us-house-5':2,'state-house-19':2,'state-house-22':2,'state-house-23':2,'state-house-24':2,
 **{'state-house-'+str(n):3 for n in [25,26,27,28,35,36,37]},'county-executive':3,'county-district-1':3,
 **{'county-district-'+str(n):4 for n in [2,3,4,6]},**{'county-at-large-'+str(n):4 for n in [1,2,3]}}
JUDGES=[
 ('supreme-court','Missouri Supreme Court','PAUL C. WILSON',5),
 ('appeals-western','Court of Appeals · Western District','LISA WHITE HARDWICK',5),
 ('circuit-16-2','Circuit 16 · Division 2','KENNETH R. GARRETT, III',5),
 ('circuit-16-4','Circuit 16 · Division 4','PATRICK C. EDWARDS',5),
 ('circuit-16-14','Circuit 16 · Division 14','LAUREN D. BARRETT',5),
 ('circuit-16-17','Circuit 16 · Division 17','CORY L. ATKINS',6),
 ('circuit-16-18','Circuit 16 · Division 18','KEVIN D. HARRELL',6),
 ('associate-16-25','Associate Circuit 16 · Division 25','ABBIE ROTHERMICH',6),
 ('associate-16-26','Associate Circuit 16 · Division 26','R. TRAVIS WILLINGHAM',6),
 ('associate-16-27','Associate Circuit 16 · Division 27','KEA S. BIRD-RILEY',6),
 ('associate-16-31','Associate Circuit 16 · Division 31','MARY FRANCES WEIR',6),
]
MEASURES=[
 ('amendment-3','Constitutional Amendment No. 3',1,3,'CONSTITUTIONAL AMENDMENT NO. 3',7),
 ('amendment-6','Constitutional Amendment No. 6',1,3,'CONSTITUTIONAL AMENDMENT NO. 6',7),
 ('amendment-7','Constitutional Amendment No. 7',2,1,'CONSTITUTIONAL AMENDMENT NO. 7',7),
 ('amendment-8','Constitutional Amendment No. 8',2,1,'CONSTITUTIONAL AMENDMENT NO. 8',8),
 ('proposition-a','Proposition A',2,1,'PROPOSITION A',8),
 ('county-question-1','Jackson County · Question 1',2,2,'QUESTION # 1',8),
 ('blue-springs-question','Blue Springs · Question',2,2,'CITY OF BLUE SPRINGS, MO',0),
 ('independence-bond-1','Independence · General Obligation Bond Question 1',2,2,'CITY OF INDEPENDENCE, MO',0),
 ('lees-summit-question',"Lee’s Summit · Question",2,2,'CITY OF LEE’S SUMMIT, MO',0),
 ('sni-valley-question','Sni Valley Fire Protection District · Question',2,3,'SNI VALLEY FIRE',0),
]

def sha(raw):return hashlib.sha256(raw).hexdigest()
def extract(path,*flags):return subprocess.run(['pdftotext',*flags,'-layout',str(path),'-'],capture_output=True,check=True,timeout=15).stdout.decode('utf-8')
def anchor_pattern(text):
 return ''.join(r'\s+' if c==' ' else r'[.,]?' if c in '.,' else re.escape(c) for c in text)
def span(text, pattern):
 matches=list(re.finditer(pattern,text,re.I))
 if len(matches)!=1:raise ValueError('nonunique_source_field:'+pattern)
 m=matches[0];return {'start':m.start(),'end':m.end(),'text':m.group()}
def page_locator(sid,page,text):return {'source_id':sid,'page':page,'reading_sha256':sha(text.encode())}
def rows_for(sid,page,text,people):
 rows=[]
 for i,entry in enumerate(people.split(';')):
  name,party=entry.split('|')
  found=span(text,anchor_pattern(name)+r'\s+'+party+r'\b')
  match=re.match('('+anchor_pattern(name)+r')\s+('+party+r')\b',found['text'],re.I)
  original_name=match.group(1)
  rows.append({'entry_id':sid+'-'+str(page)+'-'+str(found['start']), 'printed_name':original_name,
    'printed_party':match.group(2),'ballot_order':i+1,'field_span':found,
    'background_evidence':'not_admitted','person_identity':'not_merged'})
 return rows

def compile_inventory(kceb,jceb,reviewed_at):
 for path,pin in [(kceb,KPIN),(jceb,JPIN)]:
  if sha(path.read_bytes())!=pin:raise ValueError('source_version_unadmitted')
 pages={'kceb':extract(kceb).split('\f'),'jceb':extract(jceb).split('\f')}
 if len(pages['kceb'])!=9 or len(pages['jceb'])!=3:raise ValueError('page_coverage')
 columns={(page,col):extract(jceb,'-f',str(page),'-l',str(page),'-x',str(x),'-y','0','-W',str(width),'-H','1224') for page in [1,2] for col,x,width in [(1,10,254),(2,267,261),(3,533,250)]}
 sources={
 'kceb':{'publisher':'Kansas City Election Board','url':'https://drive.google.com/file/d/1K9yPQmPpIB1g9qoErahvNjTGhrBRi9A2/view','authority_page':'https://kceb.org/elections/ballot/', 'jurisdiction':'Kansas City within Jackson County','original_sha256':KPIN,'bytes':kceb.stat().st_size,'pages':8,'document_date':'2026-09-14','retrieved_utc':'2026-10-09','freshness':'retained_snapshot; current authority link rechecked 2026-10-24, current bytes not re-fetched'},
 'jceb':{'publisher':'Jackson County Election Board','url':'https://jcebmo.org/wp-content/uploads/11.03.26-Notice-of-Election-Sample-Ballot-Poster.pdf','authority_page':'https://jcebmo.org/election-information/on-the-ballot/','jurisdiction':'Jackson County outside Kansas City corporate limits','original_sha256':JPIN,'bytes':jceb.stat().st_size,'pages':2,'document_date':'2026-08-25','retrieved_utc':'2026-10-24T07:57:44.986988Z','freshness':'bytes re-fetched; match retained October 9 version'}}
 contests=[]
 for cid,label,jpage,people in CANDIDATES:
  item={'id':cid,'kind':'candidate_election','label':label,'occurrences':[]}
  for sid,page in [('kceb',K_PAGES.get(cid)),('jceb',jpage)]:
   if not page:continue
   text=pages[sid][page-1];occ={**page_locator(sid,page,text),'candidate_rows':rows_for(sid,page,text,people),'write_in':{'printed':True,'named_candidate':False,'eligible_write_in_list':'not_verified'},'source_statuses':[]}
   if sid=='kceb':
    instruction_reading=pages['kceb'][1];instruction_span=span(instruction_reading,r'VOTE FOR ONE');instruction_page=2
   else:
    col=2 if cid in {'state-house-'+str(n) for n in range(29,37)} or cid in {'county-district-'+str(n) for n in [4,5,6]} else 1
    instruction_reading=columns[page,col]
    row_start=re.search(anchor_pattern(people.split(';')[0].split('|')[0]),instruction_reading,re.I).start()
    instructions=list(re.finditer(r'\(Vote for (?:One|ONE)\)',instruction_reading[:row_start]))
    if not instructions:raise ValueError('instruction_missing:'+cid)
    m=instructions[-1];instruction_span={'start':m.start(),'end':m.end(),'text':m.group()};instruction_page=page
   occ['instruction']={'text':instruction_span['text'],'page':instruction_page,'reading_sha256':sha(instruction_reading.encode()),'span':instruction_span}
   if sid=='jceb' and cid in {'county-at-large-3','county-district-2'}:
    candidates=list(re.finditer(r'NO CANDIDATE FILED\s+REP\b',text));found=candidates[0 if cid=='county-at-large-3' else 1]
    occ['source_statuses'].append({'text':'NO CANDIDATE FILED','party':'REP','named_candidate':False,'field_span':{'start':found.start(),'end':found.end(),'text':found.group()}})
   item['occurrences'].append(occ)
  # Equal office/district/party crosswalk, no inferred person join or position.
  sets=[{re.sub(r'\W','',r['printed_name']).casefold()+'|'+r['printed_party'].upper() for r in o['candidate_rows']} for o in item['occurrences']]
  if any(s!=sets[0] for s in sets):raise ValueError('roster_conflict_requires_review:'+cid)
  contests.append(item)
 for cid,label,name,kpage in JUDGES:
  item={'id':'retention-'+cid,'kind':'judicial_retention','label':label,'occurrences':[]}
  for sid,page in [('kceb',kpage),('jceb',1)]:
   text=pages[sid][page-1];name_span=span(text,anchor_pattern(name))
   reading=columns[1,2 if kpage==5 else 3] if sid=='jceb' else text
   question_span=span(reading,r'Shall Judge\s+'+anchor_pattern(name)+r'[^?]+\?')
   item['occurrences'].append({**page_locator(sid,page,text),'printed_name':name_span['text'],'name_span':name_span,
    'wording_column':(2 if kpage==5 else 3) if sid=='jceb' else None,'wording':question_span['text'],'wording_sha256':sha(question_span['text'].encode()),'wording_reading_sha256':sha(reading.encode()),'wording_span':question_span,
    'choices':['YES','NO'],'background_evidence':'not_admitted','person_identity':'not_merged'})
  contests.append(item)
 for cid,label,page,column,anchor,kpage in MEASURES:
  reading=columns[page,column]
  marker=re.search(anchor_pattern(anchor),reading).end()
  start=re.search(r'\b(?:Shall|Should|Do the people)\b',reading[marker:]).start()+marker
  finish=reading.index('YES',start);quote=reading[start:finish].rstrip()
  item={'id':cid,'kind':'measure','label':label,'occurrences':[{'source_id':'jceb','page':page,'column':column,'crop_points':{'x':{1:10,2:267,3:533}[column],'y':0,'width':{1:254,2:261,3:250}[column],'height':1224},'choices':['YES','NO'],'wording':quote,'wording_sha256':sha(quote.encode()),'wording_reading_sha256':sha(reading.encode()),'wording_span':{'start':start,'end':start+len(quote),'text':quote}}]}
  if kpage:item['occurrences'].append({'source_id':'kceb','page':kpage,'choices':['YES','NO'],'wording_admission':'original_link_only'})
  contests.append(item)
 kinds={kind:sum(c['kind']==kind for c in contests) for kind in ['candidate_election','judicial_retention','measure']}
 slots=sum(len(c['occurrences'][0]['candidate_rows']) for c in contests if c['kind']=='candidate_election')
 if len(contests)!=55 or kinds!={'candidate_election':34,'judicial_retention':11,'measure':10} or slots!=62:raise ValueError('union_coverage_mismatch')
 return {'version':1,'election_date':'2026-11-03','reviewed_utc':reviewed_at,'source_role':'official_public_notice_inventory',
  'scope':{'printed_union_reconciled':True,'individual_ballot_styles_enumerated':False,'personal_membership':False,'eligible_write_ins_complete':False,'current_county_inventory_certified':False,'human_acceptance':'pending','rights':'factual roster and official wording for local review; no blanket republication license claimed'},
  'counts':{'printed_contests':55,**kinds,'printed_candidate_slots':62,'retention_slots':11},
  'sources':sources,'contests':contests,'extraction_notes':['KCEB text-layer State Senator heading has no visual contest; excluded after rendered-page check.','Source punctuation/case preserved per occurrence; shared contest keys do not merge people.','NO CANDIDATE FILED is a source status, not a candidate.','Both notices are public jurisdiction-wide unions, never a personal ballot.']}

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--kceb',type=Path,required=True);parser.add_argument('--jceb',type=Path,required=True);parser.add_argument('--reviewed-at',required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
 value=compile_inventory(args.kceb,args.jceb,args.reviewed_at)
 raw=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode();args.output.write_bytes(raw)
 print(json.dumps({'sha256':sha(raw),'bytes':len(raw),'counts':value['counts'],'individual_styles_complete':False,'personal_membership':False}))
