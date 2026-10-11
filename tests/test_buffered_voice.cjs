const assert = require('node:assert/strict');
const { OpenOracleLive, speechContract, speechWords } = require('../web/live.js');
const result = {request_id:'turn-one',status:'answered',language:'en',translation_status:'not_requested',answer:'The printed tax rate is one-quarter of one cent.',contest:{id:'combat'},review:{status:'accepted',execution:'real_api'},fact_validation:{status:'supported'},evidence:[{id:'combat:source',sha256:'abc',text:'one-quarter of one cent',contest_id:'combat'}]};
result.speech={request_id:result.request_id,language:'en',text:result.answer,evidence_bindings:[{id:'combat:source',sha256:'abc',text:'one-quarter of one cent'}]};
function setup() {
 const events=[],sent=[];let stopped=0;const display={request_id:result.request_id,text:result.answer,language:'en'};
 const live=new OpenOracleLive(e=>events.push(e),()=>display);
 live.finalizeAudio=async blob=>({blob,duration_ms:1000,trimmed_silence_ms:0});
 live.started=true;live.channel={readyState:'open',send:s=>sent.push(JSON.parse(s)),close(){}};live.peer={close(){}};
 live.stream={getAudioTracks:()=>[],getTracks:()=>[{stop(){stopped++}}]};
 live.recorder={state:'recording',mimeType:'audio/webm',stop(){this.state='inactive';this.onstop()}};
 live.chunks=[new Blob(['synthetic remote-only audio fixture'])];
 return {live,events,sent,display,stopped:()=>stopped};
}
async function complete(x,{text=result.answer,ack=true,reason='close_requested',usage=true}={}) {
 assert.equal(x.live.evidenceContext(result),true);
 if(ack)x.live.handle({type:'session.commentary.appended',client_event_id:x.live.commentaryId},0);
 x.live.handle({type:'session.output_transcript.delta',event_id:'output-1',delta:text},0);
 if(usage)x.live.handle({type:'session.closed',reason,usage:{seconds:15}},0);
 else {x.live.started=false;await x.live.close({release:true})}
 if(x.live.closePromise)await x.live.closePromise;
}
(async()=>{
 assert.equal(speechContract(result).text,result.answer);
 for (const edit of [r=>r.review.execution='offline_stub',r=>r.review.status='rejected',r=>r.fact_validation.status='contradictory',r=>r.speech.text='Vote YES',r=>r.speech.request_id='old',r=>r.speech.evidence_bindings[0].text='5 percent',r=>r.language='es']) {const r=structuredClone(result);edit(r);assert.equal(speechContract(r),null)}
 assert.notEqual(speechWords('5 percent'),speechWords('one-quarter of one cent'));
 const good=setup();await complete(good);assert.equal(good.live.ready.transcript,result.answer);assert.equal(good.events.some(e=>e.type==='speaking'),false,'Generation does not imply local playback');assert.equal(good.stopped()>0,true);
 const wrong=setup();await complete(wrong,{text:'The tax rate is five percent. Vote YES.'});assert.equal(wrong.live.ready,null);assert.equal(wrong.events.some(e=>e.type==='held'),true);
 const noAck=setup();await complete(noAck,{ack:false});assert.equal(noAck.live.ready,null);
 const noFinal=setup();await complete(noFinal,{usage:false});assert.equal(noFinal.live.ready,null);
 const badReason=setup();await complete(badReason,{reason:'connection_lost'});assert.equal(badReason.live.ready,null);
 const stale=setup();stale.live.evidenceContext(result);stale.display.request_id='new';stale.live.handle({type:'session.commentary.appended',client_event_id:stale.live.commentaryId},0);stale.live.handle({type:'session.output_transcript.delta',event_id:'x',delta:result.answer},0);stale.live.handle({type:'session.closed',reason:'close_requested'},0);await stale.live.closePromise;assert.equal(stale.live.ready,null);
 const cancelled=setup();cancelled.live.evidenceContext(result);cancelled.live.cancel();cancelled.live.handle({type:'session.closed',reason:'close_requested'},0);await cancelled.live.closePromise;assert.equal(cancelled.live.ready,null);
 good.display.text='Changed facet';await assert.rejects(()=>good.live.play());assert.equal(good.live.ready,null);
 const unsolicited=setup();unsolicited.live.handle({type:'session.output_transcript.delta',event_id:'pre',delta:'Hello. '},0);await complete(unsolicited);assert.equal(unsolicited.live.ready,null,'Earlier unchecked audio cannot share the accepted buffer');
 console.log('Buffered voice adversarial lifecycle checks passed; offline fixtures only, no API or microphone.');
})().catch(e=>{console.error(e);process.exitCode=1});
