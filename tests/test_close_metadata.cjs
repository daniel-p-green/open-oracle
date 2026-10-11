'use strict';
const assert=require('node:assert/strict');
const {OpenOracleLive,closedUsageMetadata}=require('../web/live.js');
const snapshot={type:'session.closed',reason:'close_requested',event_id:'PRIVATE_EVENT',session:{id:'PRIVATE_PROVIDER_IDENTIFIER',instructions:'PRIVATE_INSTRUCTIONS',client_secret:'PRIVATE_CREDENTIAL'},usage:{seconds:4,other:'PRIVATE_USAGE'},extra:'PRIVATE_EXTRA'};
const expected={type:'session.closed',reason:'close_requested',usage:{seconds:4}};
const result={request_id:'turn',status:'answered',language:'en',translation_status:'not_requested',answer:'The printed tax rate is one-quarter of one cent.',contest:{id:'combat'},review:{status:'accepted',execution:'real_api'},fact_validation:{status:'supported'},evidence:[{id:'combat:e',sha256:'sha',text:'one-quarter of one cent',contest_id:'combat'}]};
result.speech={request_id:'turn',language:'en',text:result.answer,evidence_bindings:[{id:'combat:e',sha256:'sha',text:'one-quarter of one cent'}]};
function setup(){const events=[],live=new OpenOracleLive(e=>events.push(e),()=>({request_id:'turn',text:result.answer,language:'en'}));live.finalizeAudio=async blob=>({blob,duration_ms:1});return{live,events};}
(async()=>{
 assert.deepEqual(closedUsageMetadata(snapshot),expected);assert.deepEqual(snapshot.session.id,'PRIVATE_PROVIDER_IDENTIFIER');
 for(const seconds of[undefined,null,-1,NaN,Infinity,'4'])assert.equal(closedUsageMetadata({reason:'close_requested',usage:{seconds}}).usage,undefined);
 assert.deepEqual(closedUsageMetadata({reason:'PRIVATE_REASON',session:{id:'PRIVATE_PROVIDER_IDENTIFIER'}}),{type:'session.closed',reason:'unknown'});
 assert.deepEqual(closedUsageMetadata({reason:'expired',usage:{seconds:0}}),{type:'session.closed',reason:'expired',usage:{seconds:0}});
 const normal=setup();normal.live.closePromise=Promise.resolve();normal.live.handle(snapshot,0);assert.deepEqual(normal.live.closedEvent,expected);assert.equal(normal.live.finalUsageConfirmed,true);
 const late=setup();late.live.generation=2;late.live.closingGeneration=1;let finished=0;late.live.finishClose=()=>finished++;late.live.handle(snapshot,1);assert.deepEqual(late.live.closedEvent,expected);assert.equal(finished,1);late.live.handle({...snapshot,usage:{}},0);assert.deepEqual(late.live.closedEvent,expected,'Unrelated old generation cannot replace closure metadata');
 for(const seconds of[undefined,-1,NaN,Infinity,'4']){
  const x=setup();x.live.started=true;let sent=0;x.live.channel={readyState:'open',send(value){if(JSON.parse(value).type==='session.close')sent++},close(){}};x.live.prepared=structuredClone(result.speech);x.live.commentaryAcknowledged=true;x.live.outputTranscript=result.answer;x.live.chunks=[new Blob(['offline fixture'])];
  x.live.handle({...snapshot,usage:{seconds}},0);await x.live.closePromise;assert.equal(x.live.finalUsageConfirmed,false);assert.equal(x.live.ready,null);assert.equal(x.events.some(e=>e.type==='held'),true);assert.equal(sent,0,'A received closure without valid usage must hold speech without waiting for another closure');assert.equal(x.live.lastValidation.decode,'not_attempted');
 }
 const originalFetch=global.fetch;
 try{
  global.fetch=async()=>({ok:true,status:200,json:async()=>({accepted:true,request_id:'turn',language:'en',text:result.answer,transcript:result.answer,wav_base64:Buffer.from('offline fixture').toString('base64'),report:{acknowledged:true,final_usage_confirmed:true,close_reason:'close_requested',invalid_output:false},usage:snapshot.usage,session:snapshot.session})});
  const server=setup();assert.equal(await server.live.prepareServer(result,'visitor'),true);assert.deepEqual(server.live.closedEvent,expected);assert.equal(JSON.stringify(server.live.closedEvent).includes('PRIVATE'),false);
 }finally{global.fetch=originalFetch}
 console.log('Closure metadata checks passed: allowlist, invalid usage holds, normal/late/server paths, stale generation and no duplicate close. Offline fixtures; no service validation.');
})().catch(e=>{console.error(e);process.exitCode=1});
