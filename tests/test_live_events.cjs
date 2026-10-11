const assert=require('node:assert/strict');const {OpenOracleLive}=require('../web/live.js');
(async()=>{
 const events=[],sent=[];const live=new OpenOracleLive(e=>events.push(e));
 live.channel={readyState:'open',send:s=>sent.push(JSON.parse(s)),close(){}};const track={enabled:false,stop(){this.readyState='ended'}};live.stream={getAudioTracks:()=>[track],getTracks:()=>[track]};
 assert.equal(live.send({type:'session.commentary.append'}),false);live.handle({type:'session.started'},0);assert.equal(track.enabled,true);assert.equal(sent.length,0);
 live.handle({type:'session.input_transcript.delta',delta:'Amendment '},0);live.handle({type:'session.input_transcript.delta',delta:'six'},0);assert.equal(live.transcript,'Amendment six');assert.equal(sent.length,0,'Partial transcription cannot run tools');
 const delegation={type:'session.delegation.created',delegation:{id:'fixture',target:'client'}};live.handle(delegation,0);live.handle(delegation,0);assert.equal(events.filter(e=>e.type==='review').length,1);assert.equal(track.enabled,false);assert.equal(track.readyState,'ended');assert.equal(sent[0].type,'session.input_audio.mute');
 live.handle({type:'session.output_transcript.delta',event_id:'unapproved',delta:'Unchecked generated answer'},0);assert.equal(live.ready,null);assert.equal(JSON.stringify(events).includes('Unchecked generated answer'),false);
 live.evidenceContext({status:'answered',review:{status:'accepted',execution:'offline_stub'}});assert.equal(sent.some(x=>x.type==='session.commentary.append'),false,'Stub acceptance cannot return speakable context');
 live.handle({type:'session.closed',reason:'close_requested'},0);await live.closePromise;
 const count=events.length;live.handle({type:'session.input_transcript.delta',delta:'stale'},0);assert.equal(events.length,count);assert.equal(live.ready,null);
 console.log('Offline GPT-Live events passed: no partial tool execution, duplicate delegation, immediate capture stop, no unchecked output, rejected context closes session.');
})().catch(e=>{console.error(e);process.exitCode=1});
