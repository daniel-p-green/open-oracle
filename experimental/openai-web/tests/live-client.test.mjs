import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createSession} from '../web/core.mjs';
import {createProviderClient,validateIntegratedResult} from '../web/live-client.mjs';
const corpus=JSON.parse(await readFile(new URL('../fixtures/combat.json',import.meta.url),'utf8'));
const deferred=()=>{let resolve;const promise=new Promise(r=>{resolve=r;});return {resolve,promise};};
const reading=corpus.claims.rate.text+' This is a retained public sample, not your personal ballot.';
function result(){return {explanation:corpus.claims.rate.text,claims:[{id:'rate',...corpus.claims.rate}],source:corpus.sources[0],scope:corpus.scope,reading,review:'completed_uncalibrated',playback_enabled:false,audio:{prepared:true,bytes:48000,sha256:'a'.repeat(64),transcript_match:true,finalized:true,seconds:1}};}
const ready=id=>({request_id:id,state:'ready',result:result(),expires_in_seconds:120});
function setup(overrides={},options={}){
 const received=[],states=[],cancelled=[];
 const transport={start:async id=>ready(id),poll:async id=>ready(id),cancel:async id=>{cancelled.push(id);},...overrides};
 const client=createProviderClient({session:createSession(),corpus,transport,onResult:r=>received.push(r),onState:s=>states.push(s),pollMs:0,deadlineMs:1000,...options});
 return {client,received,states,cancelled};
}
test('ready server result binds text, scope, source, complete audio metadata and disabled playback',async()=>{
 const original=result();const p=validateIntegratedResult(original,corpus);original.explanation='Vote Yes';
 const value=await p;assert.equal(value.explanation,corpus.claims.rate.text);assert.throws(()=>{value.claims[0].text='Vote Yes';},TypeError);
 const {client,received,states}=setup();await client.start();assert.equal(received.length,1);assert.equal(states.at(-1),'ready');assert.equal(received[0].playback_enabled,false);
});
test('forged scope/citation/text or incomplete audio metadata is held',async()=>{
 for(const mutate of [r=>{r.explanation='Vote Yes';},r=>{r.source={...r.source,url:'https://wrong.invalid'};},r=>{r.scope={...r.scope,election_date:'2024-11-05'};},r=>{r.claims=[];},r=>{r.audio.finalized=false;},r=>{r.playback_enabled=true;},r=>{r.reading+=' Extra words';}]){
  const r=result();mutate(r);await assert.rejects(validateIntegratedResult(r,corpus));
 }
});
test('reset while Start is in flight cancels by request ID and rejects its late result',async()=>{
 const gate=deferred();let request;
 const {client,received,cancelled}=setup({start:id=>{request=id;return gate.promise;}});
 const running=client.start();client.stop();gate.resolve(ready(request));await running;
 assert.deepEqual(received,[]);assert.deepEqual(cancelled,[request]);
});
test('reset while polling rejects late Ready without repopulating output',async()=>{
 const gate=deferred(),entered=deferred();let request;
 const {client,received}=setup({start:async id=>({request_id:id,state:'queued'}),poll:id=>{request=id;entered.resolve();return gate.promise;}});
 const running=client.start();await entered.promise;client.stop();gate.resolve(ready(request));await running;assert.deepEqual(received,[]);
});
test('server failures, held, expired and wrong request results never auto-retry or release',async()=>{
 for(const stage of ['held','expired','wrong','failure']){
  let calls=0;
  const {client,received}=setup({start:async id=>{calls++;if(stage==='failure')throw Error();return stage==='wrong'?ready('wrong-request'):{request_id:id,state:stage};}});
  await client.start();assert.equal(calls,1);assert.deepEqual(received,[]);
 }
});
test('deadline aborts fetch, requests cancellation and never publishes',async()=>{
 const {client,received,states,cancelled}=setup({start:(id,signal)=>new Promise((_,reject)=>signal.addEventListener('abort',()=>reject(Error()),{once:true}))},{deadlineMs:5});
 await client.start();assert.equal(states.at(-1),'timed_out');assert.equal(cancelled.length,1);assert.deepEqual(received,[]);
});
test('a reset triggered by Ready notification still prevents result publication',async()=>{
 let client;const received=[];
 client=createProviderClient({session:createSession(),corpus,transport:{start:async id=>ready(id),cancel:async()=>{}},onState:s=>{if(s==='ready')client.stop();},onResult:r=>received.push(r)});
 await client.start();assert.deepEqual(received,[]);
});
test('shared-session invalidation sends server cancellation even without client.stop',async()=>{
 const gate=deferred(),entered=deferred(),session=createSession(),cancelled=[];let request;
 const client=createProviderClient({session,corpus,pollMs:0,transport:{start:async id=>({request_id:id,state:'queued'}),poll:id=>{request=id;entered.resolve();return gate.promise;},cancel:async id=>cancelled.push(id)}});
 const running=client.start();await entered.promise;session.reset();gate.resolve(ready(request));await running;
 assert.deepEqual(cancelled,[request]);
});

test('prepared result expiry invalidates local readiness and sends cancellation',async()=>{
 const {client,states,cancelled}=setup({start:async id=>({...ready(id),expires_in_seconds:.005})});
 await client.start();await new Promise(done=>setTimeout(done,15));
 assert.equal(states.at(-1),'expired');assert.equal(cancelled.length,1);
});
