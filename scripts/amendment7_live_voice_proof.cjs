'use strict';
// Explicit paid public-fixture proof. Fake microphone files only; no speaker playback.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),assert=require('node:assert/strict');
const typed=process.argv.includes('--typed-input');
const repo=path.resolve(__dirname,'..'),out=path.join(repo,'.local/amendment7-voice/proof');
if(!process.argv.includes('--execute-approved')){console.log(JSON.stringify({execute:false,evidence_requests_max:2,voice_sessions_max:4,physical_microphone:false,playback:false,retries:0,reserve_usd:1.5}));process.exit(0)}
cp.execFileSync(repo+'/.venv/bin/python',['-c',`import json,fcntl,os
from pathlib import Path
p=Path('.local/live-budget-20261010.json')
with open('.local/live-budget-20261010.lock','a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);b=json.loads(p.read_text());r=b['amendment7_voice_20261011']
 assert r['status']=='reserved_plain_language_trial' and r['proof_reserved_usd']==4.8
 r['status']='proof_started_no_retry';t=p.with_suffix('.tmp');t.write_text(json.dumps(b,indent=2)+'\\n');os.replace(t,p)
`],{cwd:repo,stdio:['ignore','ignore','ignore']});
fs.mkdirSync(out,{recursive:false});
const{chromium}=require('/opt/homebrew/lib/node_modules/promptfoo/node_modules/playwright');
let server,browser,page,timer,asks=0,voices=0;const report={execution:'real_strands_decisions_gpt_live',input:typed?'typed_public_questions_after_separate_live_microphone_transport_proof':'locally_synthesized_public_question_through_generated_WebAudio_stream_started_after_connection',physical_microphone:false,playback_calls:0,retries:0,turns:[],errors:[]};
const save=()=>fs.writeFileSync(out+'/result.json',JSON.stringify(report,null,2));
(async()=>{
 timer=setTimeout(()=>{report.status='outer_deadline';save();browser?.close();server?.kill('SIGTERM')},230000);
 server=cp.spawn(repo+'/.venv/bin/python',['-B','-c','from open_oracle.server import make_server;s=make_server(port=0,live=True,live_voice=True,live_ws=True,max_live_requests=2,max_voice_sessions=4);print(s.server_port,flush=True);s.serve_forever()'],{cwd:repo,env:{...process.env,OPEN_ORACLE_ALLOW_LIVE:'1',OPEN_ORACLE_MODEL:'gpt-6-luna'},stdio:['ignore','pipe','ignore']});
 const port=await new Promise((resolve,reject)=>{const t=setTimeout(()=>reject(Error('Startup timeout')),15000);server.stdout.once('data',x=>{clearTimeout(t);const p=Number(String(x).trim());if(!Number.isInteger(p)||p<1024)return reject(Error('Port invalid'));resolve(p)});server.once('exit',()=>reject(Error('Owned server exited')))}),origin='http://127.0.0.1:'+port;
 for(const name of ['yes','no']){
  const turn={name};report.turns.push(turn);save();
  browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--autoplay-policy=no-user-gesture-required']});
  page=await browser.newPage({viewport:{width:800,height:480},reducedMotion:'reduce'});
  page.on('pageerror',e=>report.errors.push({name:e.name,category:'browser_script_error'}));
  await page.addInitScript(()=>{window.playCalls=0;HTMLMediaElement.prototype.play=()=>{window.playCalls++;throw Error('Playback forbidden in proof')};});
  await page.route('**/*',r=>{const u=new URL(r.request().url());if(u.origin!==origin)return r.abort();if(r.request().method()==='POST'){if(u.pathname==='/api/ask'&&++asks>2)return r.abort();if(u.pathname.startsWith('/api/live/')&&++voices>4)return r.abort()}return r.continue()});
  await page.goto(origin);await page.locator('#mic:enabled').waitFor();
  await page.getByText('City or district context',{exact:true}).click();await page.locator('#authority').selectOption('KCEB');await page.locator('#location').selectOption({label:'Kansas City within Jackson County'});
  if(!typed){
  const captureResponse=page.waitForResponse(r=>r.url().endsWith('/api/live/session'));
  await page.evaluate(async b64=>{
   window.voiceEvents=[];const original=live.handle.bind(live);
   live.handle=(event,generation)=>{window.voiceEvents.push({type:event.type,error_code:event.error?.code,voice:event.type==='session.started'?event.session?.audio?.output?.voice:undefined});original(event,generation);if(event.type==='session.started')window.syntheticStart?.();};
   navigator.mediaDevices.getUserMedia=async()=>{const context=new AudioContext(),destination=context.createMediaStreamDestination();const bytes=Uint8Array.from(atob(b64),c=>c.charCodeAt(0));const buffer=await context.decodeAudioData(bytes.buffer),source=context.createBufferSource();source.buffer=buffer;source.connect(destination);window.syntheticStart=async()=>{await context.resume();source.start();window.syntheticStart=null;};window.fixtureContext=context;return destination.stream;};
  },fs.readFileSync(repo+'/.local/amendment7-voice/'+name+'.wav').toString('base64'));
  await page.locator('#mic').click();const cr=await captureResponse;turn.capture_http=cr.status();save();assert.equal(cr.status(),201);
  await page.waitForFunction(()=>interaction.snapshot().state==='review',{},{timeout:45000});
  turn.events=await page.evaluate(()=>window.voiceEvents);turn.transcript=await page.locator('#question').inputValue();turn.capture_stopped=await page.evaluate(()=>!live.stream||live.stream.getTracks().every(t=>t.readyState==='ended'));
  assert.match(turn.transcript,/amendment\s+(?:7|seven)/i);assert.match(turn.transcript,name==='yes'?/taxes.*(?:go away|away)/i:/no.*mean/i);assert.equal(turn.capture_stopped,true);save();
  }else{await page.locator('#question').fill(name==='yes'?'If I vote Yes on Amendment 7, do my taxes go away?':'For Amendment 7, what does No mean?');}
  const textResponse=page.waitForResponse(r=>r.url().endsWith('/api/ask'));await page.locator('#ask-form button[type=submit]').click();const tr=await textResponse;const result=await tr.json();
  Object.assign(turn,{text_http:tr.status(),status:result.status,answer:result.answer,review:result.review,trace:result.trace,stage_ms:result.stage_ms,elapsed_ms:result.elapsed_ms,sources:result.evidence?.map(e=>({id:e.id,sha256:e.sha256})),speech_contract:!!result.speech});save();
  assert.equal(result.status,'answered');assert.equal(result.review.status,'accepted');assert.equal(result.review.execution,'real_api');assert.equal(result.evidence.length,4);assert(result.speech);
  assert.match(result.answer,name==='yes'?/No immediate tax cut/:/Existing taxes would not change/);
  await page.locator('#speak:enabled').waitFor();const speechResponse=page.waitForResponse(r=>r.url().endsWith('/api/live/speech'));await page.locator('#speak').click();const sr=await speechResponse,raw=await sr.json();
  Object.assign(turn,{speech_http:sr.status(),speech_validation:raw.report,speech_usage:raw.usage,speech_transcript:raw.transcript,remaining_voice_sessions:raw.voice_sessions_remaining});save();assert.equal(sr.status(),200);assert.equal(raw.accepted,true);
  await page.waitForFunction(()=>!!live.ready||document.getElementById('speech-status').textContent.includes('did not match'),{},{timeout:10000});
  Object.assign(turn,await page.evaluate(()=>({ready:!!live.ready,audio_bytes:live.ready?.blob.size,duration_ms:live.ready?.duration_ms,decoded:live.lastValidation?.decode,play_calls:window.playCalls,button:document.getElementById('speak').textContent,capture_usage:live.finalUsageConfirmed,interaction_state:interaction.snapshot().state})));
  assert.equal(turn.ready,true);assert.equal(turn.decoded,'succeeded');assert.equal(turn.button,'Play answer');assert.equal(turn.play_calls,0);assert.notEqual(turn.interaction_state,'speaking');
  await page.screenshot({path:out+'/'+name+'-ready-800.png'});await page.setViewportSize({width:320,height:700});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.screenshot({path:out+'/'+name+'-ready-320.png'});
  await page.getByRole('button',{name:'Erase this session',exact:true}).click();await page.waitForFunction(()=>interaction.snapshot().state==='idle');turn.erased=await page.evaluate(()=>live.ready===null&&document.getElementById('answer-region').hidden&&document.getElementById('question').value==='');assert.equal(turn.erased,true);save();await browser.close();browser=null;
 }
 report.status='passed';report.evidence_requests=asks;report.voice_sessions=voices;report.human_audibility='unverified';assert.equal(report.errors.length,0);save();console.log(JSON.stringify(report));
})().catch(async e=>{if(page&&!page.isClosed()){report.failure_state=await page.evaluate(()=>({state:interaction.snapshot().state,activity:document.getElementById('activity').textContent,transcript:document.getElementById('question').value,started:live.started,connection:live.peer?.connectionState,channel:live.channel?.readyState,events:window.voiceEvents})).catch(()=>null);await page.screenshot({path:out+'/failure.png'}).catch(()=>{});}report.status='failed';report.evidence_requests=asks;report.voice_sessions=voices;report.failure={name:e.name,message:String(e.message).slice(0,180)};save();console.log(JSON.stringify(report));process.exitCode=1}).finally(async()=>{clearTimeout(timer);await browser?.close();server?.kill('SIGTERM')});
