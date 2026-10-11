"""Fixed, bounded synthetic proof. No microphone/camera, no user conversation logging."""
import argparse
import json
import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from open_oracle.corpus import Corpus
from open_oracle.engine import EvidenceLoop
from open_oracle.orchestration import build_selector
from open_oracle.openai_integrations import DecisionsReviewer, post_openai, require_live_authorization

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--approved-spend-usd',type=float,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    require_live_authorization()
    if args.approved_spend_usd != 5 or os.environ.get('OPEN_ORACLE_MODEL') != 'gpt-6-luna':
        raise ValueError('This proof is frozen to the approved $5 total and gpt-6-luna')
    if args.output.exists(): raise ValueError('Never overwrite or repeat a prior proof')
    ledger=Path(__file__).resolve().parents[1]/'.local/live-budget-20261010.json'
    # Exclusive creation prevents accidental concurrent/repeated charged batches.
    ledger.parent.mkdir(parents=True,exist_ok=True)
    budget={'approved_total_usd':5,'prior_aws_smoke_reserve_usd':1,'this_batch_reserve_usd':1,
            'gpt_live_transport_reserve_usd':0.10,'allocated_total_usd':2.10,
            'status':'reserved_before_network','invoice_cost':'unconfirmed',
            'price_source':'https://developers.openai.com/api/docs/pricing',
            'request_limits':{'turns':3,'model_calls_per_turn':5,'model_output_tokens':600,
                              'model_message_bytes':90000,'review_calls':3,'review_payload_bytes':65536,'retries':0}}
    with ledger.open('x') as f: json.dump(budget,f,indent=2)
    calls=[]
    def review_transport(resource,payload):
        if resource!='decisions' or len(calls)>=3 or len(json.dumps(payload).encode())>65536:
            raise ValueError('Fixed review budget exceeded')
        calls.append({'resource':resource})
        raw=post_openai(resource,payload)
        calls[-1]['usage']=raw.get('usage',{})
        return raw
    reviewer=DecisionsReviewer(review_transport)
    reviewer.execution='real_api'  # This wrapper calls only the actual authorized transport.
    engine=EvidenceLoop(Corpus(),build_selector(),reviewer)
    turns=[]
    try:
        for question,expected in [('What does COMBAT say?','answered'),('What does NO mean?','answered'),
                                  ('Will COMBAT reduce crime by 50%?','insufficient_evidence')]:
            response=engine.answer(question,{'election_date':'2026-11-03','authority':'JCEB'},contest_id='combat')
            trace=response['trace']
            proved=({'resolve_contest','search_evidence','read_evidence'} <= {t['tool'] for t in trace}
                    and all(t.get('provider_execution')=='real_api' for t in trace))
            turns.append({'question':question,'expected_status':expected,'real_agent_workflow_observed':proved,'response':response})
            if response['status']!=expected or response['review']['status']!='accepted' or not proved: break
        artifact={'execution':'real_api_attempt','model':'gpt-6-luna','voice_tested':False,'turns':turns,
                  'passed':len(turns)==3 and all(t['real_agent_workflow_observed'] and t['response']['status']==t['expected_status'] and t['response']['review']['status']=='accepted' for t in turns),
                  'budget':budget,'review_transport_calls':calls}
        # Standard rates: conservative uncached input; no cache discount assumed.
        usages=[t['response']['trace'][0].get('usage',{}) for t in turns if t['response']['trace']]
        model_est=sum(u.get('inputTokens',0)*0.10/1e6+u.get('outputTokens',0)*0.50/1e6 for u in usages)
        review_est=sum(c.get('usage',{}).get('input_tokens',0)*0.10/1e6 for c in calls)
        artifact['measured_usage_estimate_usd']=model_est+review_est
        artifact['usage_complete']=len(usages)==len(turns) and all(u.get('totalTokens',0)>0 for u in usages) and all('input_tokens' in c.get('usage',{}) for c in calls)
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x') as f: json.dump(artifact,f,indent=2)
        budget.update(status='batch_stopped',measured_usage_estimate_usd=artifact['measured_usage_estimate_usd'],usage_complete=artifact['usage_complete'])
        ledger.write_text(json.dumps(budget,indent=2))
        print(json.dumps({'passed':artifact['passed'],'turns':len(turns),'output':str(args.output),'estimated_usd':artifact['measured_usage_estimate_usd'],'usage_complete':artifact['usage_complete'],
                          'last_status':turns[-1]['response']['status'],'last_review':turns[-1]['response']['review']['status']}))
    except BaseException:
        budget['status']='interrupted_cost_unconfirmed_do_not_retry'
        ledger.write_text(json.dumps(budget,indent=2))
        raise

if __name__=='__main__':main()
