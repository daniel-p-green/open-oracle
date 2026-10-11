'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..');
const python=spawnSync(path.join(root,'.venv/bin/python'),['-B','-c',`import json
from open_oracle.corpus import Corpus
from open_oracle.engine import EvidenceLoop
from open_oracle.render_catalog import rendering_catalog
c=Corpus();out=[]
for i,(q,s,contest) in enumerate([('What is COMBAT tax rate and how long would it last?',{},None),('Compare Pollard and Fields on priorities and property taxes',{},None),('Compare Pollard and Fields on property taxes and climate',{},None),('What does Yes mean?',{'authority':'KCEB'},'amendment-7'),('What does No mean?',{'authority':'JCEB'},'amendment-7'),('When will Amendment 7 eliminate taxes?',{'authority':'KCEB'},'amendment-7'),('Will COMBAT lower crime?',{},'combat'),('How should I vote on COMBAT?',{},None)]):
 s={'election_date':'2026-11-03',**s};rid='ingress-'+str(i);out.append({'context':{'scope':s,'language':'en','contest_id':contest},'ticket':{'request_id':rid,'epoch':0},'catalog':rendering_catalog(c,s),'response':EvidenceLoop(c).answer(q,s,contest_id=contest,request_id=rid)})
print(json.dumps(out))`],{cwd:root,encoding:'utf8',maxBuffer:5e6});
assert.equal(python.status,0,python.stderr);const fixtures=JSON.parse(python.stdout);
global.window=global;global.OpenOracleReleaseStore=require(path.join(root,'web/release-store.js'));
vm.runInThisContext(fs.readFileSync(path.join(root,'web/render-bindings.js'),'utf8'));
(async()=>{
 const savedFetch=global.fetch;let checks=0;
 try{
  for(const fixture of fixtures){
   let current=fixture.ticket;global.fetch=async()=>({ok:true,json:async()=>fixture.catalog});
   const ingress=OpenOracleIngress.createIngress(t=>t.request_id===current?.request_id&&t.epoch===current?.epoch);
   await ingress.prepare(fixture.ticket,fixture.context);
   const result=ingress.install(fixture.response,fixture.ticket);assert.equal(result.ok,true,result.reason);assert.equal(result.response.speech,false);assert.equal(result.response.operational_receipt,undefined);checks++;
   if(result.response.view_plan){assert.deepEqual(ingress.descriptor(result.response.view_plan,'complete',fixture.ticket),result.response.view_plan);checks++}
   ingress.invalidate('stop');assert.equal(ingress.snapshot().accepted,result.response);assert.equal(ingress.install(fixture.response,fixture.ticket).ok,false);checks++;
   ingress.invalidate('erase',{erase:true});assert.equal(ingress.snapshot().accepted,null);checks++;
  }
  const fixture=fixtures[0];global.fetch=async()=>({ok:true,json:async()=>fixture.catalog});
  const ingress=OpenOracleIngress.createIngress(()=>true);await ingress.prepare(fixture.ticket,fixture.context);
  for(const modify of [r=>{r.card.facets[1].start++},r=>{r.card.facets[2].statement='changed duration'},r=>{r.evidence[0].text='invented'},r=>{r.request_id='stale'},r=>{r.language='es'},r=>{r.scope.authority='JCEB'}]){
   const altered=structuredClone(fixture.response);modify(altered);assert.equal(ingress.install(altered,fixture.ticket).ok,false);assert.equal(ingress.snapshot().accepted,null);checks++;
  }
  let current=true,complete;global.fetch=()=>new Promise(resolve=>{complete=resolve});
  const late=OpenOracleIngress.createIngress(()=>current);const pending=late.prepare(fixture.ticket,fixture.context);current=false;complete({ok:true,json:async()=>fixture.catalog});await assert.rejects(pending,/Request stopped/);assert.equal(late.snapshot().accepted,null);checks++;
  global.fetch=async()=>({ok:false});await assert.rejects(ingress.prepare(fixture.ticket,fixture.context),/Source definitions unavailable/);checks++;
  console.log(JSON.stringify({passed:checks,fixture_count:fixtures.length,providers:0,capture:0,execution:'canonical_python_and_node_contracts'}));
 }finally{global.fetch=savedFetch;delete global.window;delete global.OpenOracleReleaseStore;delete global.OpenOracleIngress}
})().catch(e=>{console.error(e);process.exitCode=1});
