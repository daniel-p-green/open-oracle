'use strict';
// Every event, PCM sample and transport callback here is synthetic. No sound I/O.
const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const root = process.env.OPEN_ORACLE_ROOT;
assert(root, 'Set OPEN_ORACLE_ROOT to the read-only canonical repository');
const {speechContract, speechWords} = require(path.join(root, 'web/live.js'));
const {SpeechBuffer} = require(path.join(root, 'scripts/live-ws/ws-buffer.cjs'));
const {ContinuousVoice, RELEASE} = require('./client.cjs');
const fixtures = require('./proof/synthetic-fixtures.json');
assert.equal(fixtures.synthetic, true);
const clone = value => structuredClone(value);
const deferred = () => { let resolve, reject; const promise = new Promise((a, b) => { resolve = a; reject = b; }); return {promise, resolve, reject}; };
const flush = async () => { for (let i = 0; i < 12; i++) await Promise.resolve(); };

function buffered(contract, {close = true, extra = '', duplicate = false, ack = true} = {}) {
  const gate = new SpeechBuffer(contract.text, 'SYNTHETIC-commentary');
  if (ack) gate.event({type: 'session.commentary.appended', client_event_id: 'SYNTHETIC-commentary'});
  gate.event({type: 'session.output_transcript.delta', event_id: 'SYNTHETIC-output', delta: contract.text + extra});
  const pcm = Buffer.alloc(960); for (let i = 0; i < pcm.length; i += 2) pcm.writeInt16LE(1000, i);
  const event = {type: 'session.output_audio.delta', event_id: 'SYNTHETIC-audio', delta: pcm.toString('base64')};
  gate.event(event); if (duplicate) gate.event(event);
  if (close) gate.event({type: 'session.closed', reason: 'close_requested', usage: {seconds: .02}});
  const output = gate.finish(); gate.clear(); return output;
}

class FakeAdapter {
  constructor() {
    this.sequence = 0; this.captures = []; this.requests = []; this.renders = []; this.plays = [];
    this.nextAsk = this.nextRender = this.nextCapture = this.nextEcho = null;
  }
  async control(action, context) { return {...context}; }
  async complete() { return true; }
  clearDocument(document) { document?.localBytes?.fill(0); }
  verifyFinal(event, lease) {
    return event.finality?.kind === 'SYNTHETIC_ONLY'
      && ['epoch', 'generation', 'capture_id', 'transcript_id'].every(k => event.finality[k] === event[k])
      && event.capture_id === lease.capture_id;
  }
  async settleEcho() {
    if (this.nextEcho) { const pending = this.nextEcho; this.nextEcho = null; return pending.promise; }
    return true; // Authored proof placeholder; never physical echo evidence.
  }
  async openCapture(lease, callbacks, signal) {
    const handle = {lease, callbacks, signal, closed: false, close() { this.closed = true; }};
    this.captures.push(handle);
    if (this.nextCapture) { const pending = this.nextCapture; this.nextCapture = null; await pending.promise; }
    return handle;
  }
  receipt(ticket, ordinal = 0) {
    const result = clone(fixtures.turns[ordinal % 2].result);
    result.request_id = result.speech.request_id = ticket.request_id;
    return {result, ticket: {...ticket, release_id: `SYNTHETIC-release-${++this.sequence}`,
      speech_id: `SYNTHETIC-speech-${this.sequence}`, playback_id: `SYNTHETIC-playback-${this.sequence}`}};
  }
  async ask(input, signal) {
    this.requests.push({input, signal});
    if (this.nextAsk) { const pending = this.nextAsk; this.nextAsk = null; return pending.promise; }
    return this.receipt(input.ticket, this.requests.length - 1);
  }
  media(ticket, ordinal) {
    if (ordinal === undefined) ordinal = Math.max(0, this.requests.findIndex(r => r.input.ticket.request_id === ticket.request_id));
    const result = clone(fixtures.turns[ordinal % 2].result);
    result.request_id = result.speech.request_id = ticket.request_id;
    const contract = speechContract(result), output = buffered(contract);
    assert.equal(output.accepted, true);
    return {ticket: {...ticket}, request_id: contract.request_id, text: contract.text, language: contract.language,
      transcript: output.transcript, audio: new Uint8Array(output.wav), report: output.report, usage: {seconds: .02}};
  }
  async render(ticket, signal) {
    this.renders.push({ticket, signal});
    if (this.nextRender) { const pending = this.nextRender; this.nextRender = null; return pending.promise; }
    return this.media(ticket);
  }
  play(media, ticket, callbacks, signal) {
    const handle = {media, ticket, callbacks, signal, cancelled: false, cancel() { this.cancelled = true; }};
    this.plays.push(handle); return handle; // Does NOT output sound.
  }
}

function setup(maxTurns = 4) {
  const adapter = new FakeAdapter(), clock = {value: 0}, states = []; let ids = 0;
  const controller = new ContinuousVoice({adapter, speechContract, speechWords, id: () => `SYNTHETIC-id-${++ids}`,
    now: () => clock.value, setTimer: () => 'SYNTHETIC-watchdog', clearTimer: () => {},
    notify: event => states.push(event), maxTurns});
  controller.document = {synthetic: true, localBytes: new Uint8Array([1, 2])};
  return {adapter, controller, clock, states};
}
function finalEvent(controller, text = fixtures.turns[0].question, transcript = 'SYNTHETIC-transcript-1') {
  const event = {...controller.lease, transcript_id: transcript, text};
  event.finality = {kind: 'SYNTHETIC_ONLY', ...Object.fromEntries(['epoch', 'generation', 'capture_id', 'transcript_id'].map(k => [k, event[k]]))};
  return event;
}
async function spokenTurn(controller, adapter, ordinal = 1) {
  assert.equal(controller.inputFinal(finalEvent(controller, fixtures.turns[(ordinal - 1) % 2].question,
    `SYNTHETIC-transcript-${ordinal}`), controller.lease), true);
  await flush(); return adapter.plays.at(-1);
}

test('two source-checked turns follow one Start without confirm or manual Play', async () => {
  const {controller: c, adapter: a} = setup(2);
  assert.equal(await c.start(), true);
  for (let i = 1; i <= 2; i++) {
    const capture = a.captures.at(-1), player = await spokenTurn(c, a, i);
    assert.equal(capture.closed, true); assert.equal(c.state, 'playing_pending');
    assert.equal(c.counts.played, i - 1); // Generation is not audible playback.
    player.callbacks.started(); player.callbacks.started(); assert.equal(c.counts.played, i);
    assert.equal(c.state, 'speaking'); player.callbacks.ended(); await flush();
  }
  assert.equal(c.state, 'exhausted'); assert.equal(a.requests.length, 2); assert.equal(a.plays.length, 2);
  assert.equal(c.counts.starts, 1); assert.equal(c.counts.completed, 2);
  assert.notEqual(a.requests[0].input.question, a.requests[1].input.question);
  assert.notEqual(a.plays[0].ticket.playback_id, a.plays[1].ticket.playback_id);
  assert.equal(a.requests.every(r => r.signal.aborted), true);
  assert.equal(a.captures.every(h => h.closed), true);
});

test('missing finality adapter disables Start; partial/delegation/quiet never request', async () => {
  const {controller: c, adapter: a} = setup(); a.verifyFinal = null;
  assert.equal(await c.start(), false); assert.equal(c.state, 'blocked'); assert.equal(a.captures.length, 0);
  const {controller: d, adapter: b} = setup(); await d.start();
  d.inputDelta({...d.lease, text: 'SYNTHETIC partial'}, d.lease);
  for (const kind of ['session.input_transcript.delta', 'session.delegation.created', 'silence_timeout']) {
    const event = finalEvent(d); event.finality.kind = kind;
    assert.equal(d.inputFinal(event, d.lease), false);
  }
  assert.equal(b.requests.length, 0); d.stop();
});

test('no echo/self-output capture during requests/render/playback; old capture rejected next turn', async () => {
  const {controller: c, adapter: a} = setup(); await c.start();
  const lease = {...c.lease}, event = finalEvent(c); const player = await spokenTurn(c, a);
  assert.equal(c.inputFinal(event, lease), false); assert.equal(a.requests.length, 1);
  player.callbacks.started(); player.callbacks.ended(); await flush();
  assert.notEqual(c.lease.capture_id, lease.capture_id);
  assert.equal(c.inputFinal(event, lease), false); assert.equal(a.requests.length, 1); c.stop();
});

test('Stop preserves document and accepted text, cancels playback, and requires deliberate Resume', async () => {
  const {controller: c, adapter: a} = setup(); await c.start();
  const player = await spokenTurn(c, a), document = c.document, accepted = clone(c.accepted), oldGeneration = c.generation;
  player.callbacks.started(); const bytes = player.media.audio; c.stop();
  assert.equal(c.state, 'paused'); assert.equal(player.cancelled, true); assert.equal(player.signal.aborted, true);
  assert.equal(bytes.every(x => x === 0), true); assert.equal(player.media.audio, null);
  assert.equal(c.document, document); assert.deepEqual(c.accepted, accepted);
  player.callbacks.ended(); player.callbacks.started(); await flush(); assert.equal(c.state, 'paused');
  assert.equal(await c.start(), false); assert.equal(await c.resume(), true); assert(c.generation > oldGeneration); c.stop();
});

test('late research after Stop/Resume cannot overwrite preserved display or render', async () => {
  const {controller: c, adapter: a} = setup(); await c.start();
  const pending = deferred(); a.nextAsk = pending;
  c.inputFinal(finalEvent(c), c.lease); const oldTicket = {...c.active};
  c.stop(); await c.resume();
  pending.resolve(a.receipt(oldTicket)); await flush();
  assert.equal(c.state, 'listening'); assert.equal(c.accepted, null); assert.equal(a.renders.length, 0); c.stop();
});

test('late rendered audio after Erase is wiped; erased callbacks cannot restore content', async () => {
  const {controller: c, adapter: a} = setup(); await c.start();
  const pending = deferred(); a.nextRender = pending;
  c.inputFinal(finalEvent(c), c.lease); await flush(); const oldTicket = {...c.active}, epoch = c.epoch;
  const documentBytes = c.document.localBytes;
  c.erase(); assert.equal(c.document, null); assert.equal(c.accepted, null); assert.notEqual(c.epoch, epoch);
  assert(documentBytes.every(x => x === 0));
  const media = a.media(oldTicket), bytes = media.audio; pending.resolve(media); await flush();
  assert.equal(media.audio, null); assert(bytes.every(x => x === 0)); assert.equal(a.plays.length, 0);
  assert.equal(c.state, 'idle'); assert.equal(await c.resume(), false);
});

test('delayed permission resource is closed after Stop; no ambient restart', async () => {
  const {controller: c, adapter: a} = setup(); const pending = deferred(); a.nextCapture = pending;
  const starting = c.start(); await flush(); c.stop(); pending.resolve(); await starting;
  assert.equal(a.captures[0].closed, true); assert.equal(c.capture, null); assert.equal(c.state, 'paused');
});

test('touch interruption cancels pending sound and opens a new generation after echo settling', async () => {
  const {controller: c, adapter: a} = setup(); await c.start();
  const player = await spokenTurn(c, a); player.callbacks.started(); const old = {...player.ticket};
  assert.equal(await c.interrupt(), true); assert.equal(player.cancelled, true); assert.equal(c.state, 'listening');
  player.callbacks.ended(); player.callbacks.started(); await flush(); assert.equal(c.state, 'listening');
  assert(c.generation > old.generation); c.stop();
});

test('echo settling refusal or timeout fails closed without opening capture', async () => {
  const {controller: c, adapter: a} = setup(); a.settleEcho = async () => false;
  assert.equal(await c.start(), false); assert.equal(a.captures.length, 0); assert.equal(c.state, 'paused');
  const {controller: d, adapter: b, clock} = setup(); const pending = deferred(); b.nextEcho = pending;
  const started = d.start(); clock.value = 5000; assert.equal(d.tick(), true);
  pending.resolve(true); await started; assert.equal(b.captures.length, 0); assert.equal(d.state, 'paused');
});

test('canonical client gate rejects unchecked, mutated, wrong-request or wrong-generation releases', async () => {
  const mutations = [r => r.result.review.execution = 'offline_stub', r => r.result.review.status = 'rejected',
    r => r.result.answer = 'SYNTHETIC unchecked extra claim', r => r.result.speech.evidence_bindings[0].sha256 = 'bad',
    r => r.ticket.generation++, r => r.ticket.request_id = 'wrong', r => r.ticket.playback_id = r.ticket.speech_id];
  for (const mutate of mutations) {
    const {controller: c, adapter: a} = setup(); await c.start();
    a.ask = async ({ticket}) => { const r = a.receipt(ticket); mutate(r); return r; };
    c.inputFinal(finalEvent(c), c.lease); await flush();
    assert.equal(c.state, 'paused'); assert.equal(c.accepted, null); assert.equal(a.plays.length, 0);
  }
});

test('closed transcript/ack/usage and strict WAV validation gate all automatic playback', async () => {
  const mutations = [m => m.ticket.speech_id = 'wrong', m => m.ticket.playback_id = 'wrong',
    m => m.text += ' extra', m => m.transcript += ' extra', m => m.report.acknowledged = false,
    m => m.report.final_usage_confirmed = false, m => m.report.close_reason = 'connection_lost',
    m => m.report.invalid_output = true, m => m.usage.seconds = NaN,
    m => m.audio[0] = 0, m => m.audio = new Uint8Array(4320046)];
  for (const mutate of mutations) {
    const {controller: c, adapter: a} = setup(); await c.start();
    a.render = async ticket => { const media = a.media(ticket); mutate(media); return media; };
    c.inputFinal(finalEvent(c), c.lease); await flush();
    assert.equal(c.state, 'paused'); assert.equal(a.plays.length, 0); assert(c.accepted); // Accepted text survives speech failure.
  }
});

test('existing SpeechBuffer withholds partial closure, duplicate audio, extra output and missing ack', () => {
  const contract = speechContract(fixtures.turns[0].result);
  for (const options of [{close: false}, {extra: ' extra'}, {duplicate: true}, {ack: false}])
    assert.equal(buffered(contract, options).accepted, false);
  assert.equal(buffered(contract).accepted, true);
});

test('deadlines abort research and prevent delayed playback; budget survives Stop/Resume', async () => {
  const {controller: c, adapter: a, clock} = setup(2); await c.start();
  const pending = deferred(); a.nextAsk = pending; c.inputFinal(finalEvent(c), c.lease);
  const ticket = {...c.active}; clock.value = 75000; assert.equal(c.tick(), true);
  pending.resolve(a.receipt(ticket)); await flush(); assert.equal(a.plays.length, 0);
  assert.equal(c.attempts, 1); await c.resume(); const player = await spokenTurn(c, a, 2); player.callbacks.started();
  c.stop(); assert.equal(c.attempts, 2); assert.equal(await c.resume(), false);
});

test('session time is bounded across pauses; input remains usable through separate core text fallback', async () => {
  const {controller: c, clock} = setup(); await c.start(); c.stop(); clock.value = 180000;
  assert.equal(await c.resume(), false); assert.equal(c.state, 'paused'); c.erase(); assert.equal(await c.start(), true); c.stop();
});

test('notify/metrics contain no transcript, content, identifiers or PCM', async () => {
  const {controller: c, adapter: a, states} = setup(); await c.start();
  const player = await spokenTurn(c, a); player.callbacks.started(); c.stop();
  assert(states.every(e => Object.keys(e).join() === 'state'));
  assert(Object.values(c.metrics()).every(v => Number.isInteger(v) && v >= 0));
  assert(!JSON.stringify({states, metrics: c.metrics()}).includes('COMBAT'));
  assert(!JSON.stringify({states, metrics: c.metrics()}).includes('SYNTHETIC-id'));
  assert.equal(RELEASE.length, 8);
});

test('late completion/permission controls and deadline events cannot reopen capture', async () => {
  const {controller: c, adapter: a, clock} = setup();
  const pending = deferred(); a.control = () => pending.promise;
  const starting = c.start(); const context = c.context(); c.stop();
  pending.resolve(context); await starting; assert.equal(a.captures.length, 0);
  const {controller: d, adapter: b, clock: time} = setup(); await d.start();
  const rendered = deferred(); b.nextRender = rendered;
  d.inputFinal(finalEvent(d), d.lease); await flush(); const ticket = {...d.active};
  time.value = 75001; const media = b.media(ticket), bytes = media.audio;
  rendered.resolve(media); await flush(); assert.equal(b.plays.length, 0);
  assert(bytes.every(x => x === 0)); assert.equal(d.state, 'paused');
});

test('reused finalized transcript cannot cause a second request in a new capture', async () => {
  const {controller: c, adapter: a} = setup(); await c.start();
  const player = await spokenTurn(c, a); player.callbacks.started(); player.callbacks.ended(); await flush();
  assert.equal(c.inputFinal(finalEvent(c), c.lease), false); assert.equal(a.requests.length, 1); c.stop();
});

test('normal completion disposes the player, and missing completion ack pauses instead of capturing', async () => {
  const {controller: c, adapter: a} = setup(); await c.start(); a.complete = async () => false;
  const player = await spokenTurn(c, a); player.callbacks.started(); player.callbacks.ended(); await flush();
  assert.equal(player.cancelled, true); assert.equal(c.state, 'paused'); assert.equal(a.captures.length, 1);
});
