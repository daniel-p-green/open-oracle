'use strict';
// Execute canonical voice boundaries with synthetic events; never acquire media.
const fs = require('node:fs'), path = require('node:path');
const deny = () => { throw Error('Offline eval network forbidden'); };
for (const name of ['node:net', 'node:tls', 'node:http', 'node:https']) {
  const api = require(name);
  for (const key of ['connect', 'createConnection', 'request', 'get', 'createServer']) if (key in api) api[key] = deny;
}
globalThis.fetch = deny;
globalThis.WebSocket = class { constructor() { deny(); } };
const root = path.resolve(process.argv[2]);
const {SpeechBuffer, words} = require(path.join(root, 'scripts/live-ws/ws-buffer.cjs'));
const {OpenOracleLive, speechWords, speechContract, closedUsageMetadata} = require(path.join(root, 'web/live.js'));
const cases = JSON.parse(fs.readFileSync(0, 'utf8'));
const texts = {
  en: 'The tax is 0.25 cent for 10 years. A NO vote does not approve the proposal.',
  es: 'El impuesto es 0.25 centavo durante 10 años. Un voto NO no aprueba la propuesta.',
  vi: 'Thuế là 0.25 xu trong 10 năm. Phiếu NO không chấp thuận đề xuất.',
  ar: 'الضريبة 0.25 سنت لمدة 10 سنوات. التصويت NO لا يوافق على المقترح.',
  'zh-Hans': '税额为 0.25 美分，持续 10 年。NO 票不批准该提案。',
  fil: 'Ang buwis ay 0.25 sentimo sa loob ng 10 taon. Ang boto na NO ay hindi nag-aapruba sa panukala.'
}; // Authored synthetic strings, not reviewed translation or actual ballot wording.

function bufferResult(text, transcript, operation) {
  const buffer = new SpeechBuffer(text, 'fixture-commentary');
  if (operation !== 'speech_missing_ack') buffer.event({type:'session.commentary.appended', client_event_id:'fixture-commentary'});
  buffer.event({type:'session.output_transcript.delta', event_id:'fixture-transcript', delta:transcript});
  if (operation === 'speech_duplicate_event') buffer.event({type:'session.output_transcript.delta', event_id:'fixture-transcript', delta:transcript});
  const pcm = Buffer.alloc(480); for (let offset=0; offset<pcm.length; offset+=2) pcm.writeInt16LE(operation === 'speech_silence' ? 0 : 1000, offset);
  buffer.event({type:'session.output_audio.delta', delta:pcm.toString('base64')});
  if (operation !== 'speech_missing_closure') buffer.event({type:'session.closed', reason:'close_requested', usage:operation==='speech_unknown_usage'?{}:{seconds:0.01}});
  const result = buffer.finish(); buffer.clear();
  return result.accepted ? 'accepted' : 'held';
}

async function run(c) {
  let actual;
  const text = texts[c.language], op = c.operation;
  const start = performance.now();
  if (op.startsWith('speech_') && op !== 'speech_language_gate') {
    let transcript = text;
    const changes = {speech_sign_change:['0.25','−0.25'], speech_spaced_sign_change:['0.25','- 0.25'],
      speech_plus_change:['0.25','+0.25'], speech_decimal_change:['0.25','0,25'],
      speech_number_change:['0.25','25'], speech_year_change:['10','20'],
      speech_polarity_change:['NO','YES']};
    if (changes[op]) transcript = transcript.replace(...changes[op]);
    if (op === 'speech_extra_advice') transcript += ' You should vote YES.';
    if (op === 'speech_truncated') transcript = transcript.slice(0, -10);
    if (op === 'speech_negation_drop') transcript = transcript.replace('does not', 'does');
    if (op === 'speech_prose_punctuation') transcript = text.replace(/\./g, '!');
    const parity = words(transcript) === speechWords(transcript) && words(text) === speechWords(text);
    actual = parity ? bufferResult(text, transcript, op) : 'comparator_parity_failed';
  } else if (op === 'delegation_freeze_duplicate') {
    const events=[], live=new OpenOracleLive(e=>events.push(e));
    live.handle({type:'session.input_transcript.delta',delta:'Synthetic question'},0);
    const event={type:'session.delegation.created',delegation:{target:'client',id:'fixture'}};
    live.handle(event,0);live.handle(event,0);live.handle({type:'session.input_transcript.delta',delta:' stale mutation'},0);
    actual=events.filter(e=>e.type==='review').length===1 && live.transcript==='Synthetic question'?'single_frozen_review':'unsafe_delegation';
    live.discardVisitor();
  } else if (op === 'playback_stale_callback') {
    const events=[], live=new OpenOracleLive(e=>events.push(e));
    let current={request_id:'synthetic-request',text,language:c.language};
    live.currentDisplay=()=>current;live.ready={contract:{...current},blob:new Blob(['fixture'])};
    const oldAudio=globalThis.Audio;
    let player;
    globalThis.Audio=class {constructor(){player=this;this.paused=true;}play(){this.paused=false;this.onplaying?.();return Promise.resolve();}pause(){this.paused=true;}removeAttribute(){}load(){}};
    try {
      await live.play(); const late=player.onplaying;
      live.cancelPlayback(); const before=events.length;
      current={request_id:'changed-request',text:'Changed',language:c.language}; late();
      actual=events.length===before&&live.ready===null&&player.paused?'stale_rejected':'stale_accepted';
    } finally {globalThis.Audio=oldAudio;live.discardVisitor();}
  } else if (op === 'privacy_erase_clear') {
    const live=new OpenOracleLive(()=>{});live.transcript='PRIVATE_CANARY';live.outputTranscript='PRIVATE_CANARY';
    live.fragments=[{delta:'PRIVATE_CANARY'}];live.pendingDelegation='PRIVATE_PROVIDER_ID';live.delegations.add('PRIVATE_PROVIDER_ID');
    live.chunks=[new Blob(['PRIVATE_CANARY'])];live.bufferBytes=14;live.discardVisitor();
    actual=!live.transcript&&!live.outputTranscript&&!live.fragments.length&&!live.chunks.length&&!live.pendingDelegation&&!live.delegations.size?'cleared':'retained';
  } else if (op === 'privacy_usage_projection') {
    const metadata=closedUsageMetadata({type:'session.closed',id:'PRIVATE_PROVIDER_ID',reason:'PRIVATE_CANARY',usage:{seconds:1,raw:'PRIVATE_CANARY'},session:{raw:'PRIVATE_CANARY'}});
    actual=JSON.stringify(metadata)==='{"type":"session.closed","reason":"unknown","usage":{"seconds":1}}'?'allowlisted':'leaked';
  } else if (op === 'speech_language_gate') {
    const evidence={id:'synthetic-source',sha256:'0'.repeat(64),text:'Synthetic retained original',contest_id:'synthetic-contest'};
    const result={status:'answered',request_id:'synthetic-request',answer:text,language:c.language,translation_status:c.language==='en'?'not_requested':'reviewed',
      review:{execution:'real_api',status:'accepted'},fact_validation:{status:'supported'},contest:{id:'synthetic-contest'},evidence:[evidence],
      speech:{request_id:'synthetic-request',text,language:c.language,evidence_bindings:[evidence]}};
    // The execution marker itself is synthetic here, never evidence of a provider call.
    actual=speechContract(result)?'accepted_contract':'held_contract';
  } else throw Error('Unknown fixed voice case');
  return {case_id:c.id, actual, elapsed_ms:performance.now()-start};
}
(async()=>{const results=[];for(const c of cases)results.push(await run(c));process.stdout.write(JSON.stringify(results));})().catch(()=>{process.stderr.write('Fixed voice contract failed\n');process.exitCode=1;});
