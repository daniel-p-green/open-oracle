'use strict';
const fs=require('node:fs'),path=require('node:path'),{randomUUID}=require('node:crypto');
const{SpeechBuffer,words}=require('./ws-buffer.cjs'),{LiveEventJournal}=require('./event-observer.cjs');
const instructions='You are Open Oracle, a neutral election evidence interface. Never recommend how to vote or invent facts. Delegate every substantive election question to the application. Ask for missing contest or jurisdiction context. Application evidence is a dated snapshot, not personal eligibility. Stay silent until the application sends approved commentary. Never greet, acknowledge, backchannel, or narrate progress. Read the approved English text exactly once without paraphrasing or adding words. All generated speech is buffered by the application and withheld unless the completed transcript matches the source-checked display.';
async function render(text){
 if(process.env.OPEN_ORACLE_ALLOW_LIVE!=='1'||!process.env.OPENAI_API_KEY)throw Error('Live authorization unavailable');
 let OpenAI,LiveWS;
 try{OpenAI=require('openai');({LiveWS}=require('openai/resources/live/ws'));}
 catch{const sdkRoot=process.env.OPEN_ORACLE_NODE_DEPENDENCIES||'/opt/homebrew/lib/node_modules/promptfoo/node_modules';OpenAI=require(path.join(sdkRoot,'openai'));({LiveWS}=require(path.join(sdkRoot,'openai/resources/live/ws')));}
 const commentaryId=randomUUID(),buffer=new SpeechBuffer(text,commentaryId),journal=new LiveEventJournal({approvedContent:text,maxEntries:256});
 return await new Promise(resolve=>{let ws,pump,deadline,quiet,closing=false,finished=false,started=false,inputFrames=0;
  const result=()=>{if(finished)return;finished=true;for(const timer of[pump,deadline,quiet])clearTimeout(timer);const final=buffer.finish();resolve({...final,journal:journal.snapshot(),input_frames:inputFrames,synthetic_input:true,microphone:false,playback:false,retries:0});buffer.clear();try{ws?.close()}catch{}};
  const send=e=>{if(finished||!ws)return;try{ws.send(e);if(e.type!=='session.input_audio.append')journal.event('sent',e)}catch{buffer.invalid=true;result()}};
  const close=()=>{if(closing||finished)return;closing=true;clearInterval(pump);clearTimeout(quiet);send({type:'session.close',event_id:randomUUID()});clearTimeout(deadline);deadline=setTimeout(result,12000)};
  try{ws=new LiveWS(new OpenAI({maxRetries:0}),{maxQueueSize:8,handshakeTimeout:15000,maxPayload:512*1024});}catch{buffer.invalid=true;result();return;}
  deadline=setTimeout(close,45000);
  ws.socket.on('open',()=>send({type:'session.start',event_id:randomUUID(),session:{model:'gpt-live-1',instructions,audio:{format:{type:'audio/pcm',rate:24000},output:{voice:'marin'}},delegation:{type:'client'},store:false}}));
  ws.on('event',e=>{if(finished)return;if(e.type!=='session.output_audio.delta')journal.event('received',e);buffer.event(e);
   if(e.type==='session.started'&&!started){started=true;const zero=Buffer.alloc(960).toString('base64');pump=setInterval(()=>{inputFrames+=480;send({type:'session.input_audio.append',audio:zero})},20);send({type:'session.input_audio.mute',event_id:randomUUID()});send({type:'session.commentary.append',event_id:commentaryId,delegation_id:null,content:text});}
   // Audio continues to include silence. Only transcript progression schedules closure.
   if(e.type==='session.output_transcript.delta'){clearTimeout(quiet);const actual=words(buffer.transcript),expected=words(text);if(!expected.startsWith(actual)){buffer.invalid=true;close();}else if(actual===expected)quiet=setTimeout(close,1500);}
   if(buffer.invalid&&!closing)close();if(e.type==='session.closed')result();
  });
  ws.on('error',()=>{buffer.invalid=true;journal.mark('websocket_error',{error_type:'ProviderOrTransportError'});if(started)close();else result();});
  ws.socket.on('close',()=>{if(!finished)result()});
 });
}
module.exports={render};
if(require.main===module){
 if(process.argv.includes('--trusted-stdin')){let input='';process.stdin.setEncoding('utf8');process.stdin.on('data',s=>{input+=s;if(input.length>4096)process.exit(2)});process.stdin.on('end',async()=>{try{const obj=JSON.parse(input);const r=await render(obj.text);const publicResult={accepted:r.accepted,report:r.report,transcript:r.transcript,usage:r.report.final_usage_confirmed?{seconds:r.journal.events.find(e=>e.type==='session.closed')?.usage_seconds}:null,wav_base64:r.accepted?r.wav.toString('base64'):null};process.stdout.write(JSON.stringify(publicResult));}catch{process.stdout.write(JSON.stringify({accepted:false,error_type:'SpeechUnavailable'}));process.exitCode=1;}});
 }else if(process.argv.includes('--execute-approved')){const repo='/Users/danielgreen/Documents/Codex/open-oracle',b=JSON.parse(fs.readFileSync(repo+'/.local/live-budget-20261010.json'));if(b.live_ws_third_status!=='reserved_one_trial'||b.live_ws_third_reserve_usd!==.15)throw Error('WebSocket trial not reserved');const output=path.join(__dirname,'real-ws-03');fs.mkdirSync(output,{recursive:false});render('The printed tax rate is one-quarter of one cent.').then(r=>{const result={execution:'real_gpt_live_websocket',...r,wav:undefined,media_saved:false,human_audibility:'unverified; playback forbidden'};fs.writeFileSync(path.join(output,'result.json'),JSON.stringify(result,null,2));console.log(JSON.stringify({accepted:r.accepted,validation:r.report,transcript:r.transcript,input_frames:r.input_frames,errors:r.journal.events.filter(e=>e.type==='error')}));});
 }else console.log(JSON.stringify({execute:false,model:'gpt-live-1',transport:'primary_websocket',sessions:1,retries:0,reserve_usd:.15,microphone:false,playback:false,media_saved:false,max_pcm_bytes:4320000,max_run_seconds:57}));
}
