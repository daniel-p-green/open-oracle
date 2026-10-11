'use strict';
const assert=require('node:assert/strict'),{checkedQuestionFlow}=require('../web/live.js');
// An authored protocol fixture, never a server release or provider acceptance.
const source={id:'fixture',sha256:'hash',text:'exact',contest_id:'contest'};
const result={request_id:'r',status:'answered',review:{status:'accepted',execution:'real_api'},fact_validation:{status:'supported'},language:'en',translation_status:'not_requested',contest:{id:'contest'},answer:'Exact answer.',evidence:[source],speech:{request_id:'r',text:'Exact answer.',language:'en',evidence_bindings:[{id:'fixture',sha256:'hash',text:'exact'}]}};
(async()=>{let checks=0;
 async function run({at,mode='ok'}={}){let current=true,ready=false,events=[];const step=name=>{events.push(name);if(at===name)current=false};const outcome=await checkedQuestionFlow({current:()=>current,finishInput:async()=>{step('input');return {text:mode==='empty'?'':'question',final:mode!=='unclosed'}},requestAnswer:async()=>{step('answer');return mode==='rejected'?{...result,review:{status:'rejected',execution:'real_api'}}:mode==='mismatch'?{...result,speech:{...result.speech,text:'wrong'}}:result},prepare:async()=>{step('prepare');ready=true;return mode!=='audioheld'},play:async()=>{step('play');if(mode==='browserblocked')throw Error('NotAllowedError')},canHear:()=>ready});return{outcome,events}}
 assert.deepEqual(await run(),{outcome:'playing',events:['input','answer','prepare','play']});checks++;
 for(const mode of ['empty','unclosed']){assert.deepEqual(await run({mode}),{outcome:'input_held',events:['input']});checks++}
 for(const mode of ['rejected','mismatch']){assert.deepEqual(await run({mode}),{outcome:'answer_held',events:['input','answer']});checks++}
 for(const at of ['input','answer','prepare','play']){const x=await run({at});assert.equal(x.outcome,'cancelled');assert.equal(x.events.at(-1),at);checks++}
 assert.equal((await run({mode:'audioheld'})).outcome,'audio_held');checks++;
 assert.equal((await run({mode:'browserblocked'})).outcome,'hear_fallback');checks++;
 console.log(JSON.stringify({synthetic_checks:checks,providers:0,microphone:0,playback:0,real_release:false}));
})().catch(e=>{console.error(e);process.exitCode=1});
