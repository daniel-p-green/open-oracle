'use strict';
// Isolated orchestration seam. No DOM, fetch, media, provider or visual changes.
const BASE = ['epoch', 'generation', 'turn_id', 'transcript_id', 'request_id'];
const RELEASE = [...BASE, 'release_id', 'speech_id', 'playback_id'];
const same = (a, b, keys) => !!a && !!b && keys.every(k => a[k] === b[k]);
const identity = (a, b) => same(a, b, ['epoch', 'generation']);
const textId = value => typeof value === 'string' && value.length > 0 && value.length <= 128;
const wipe = media => {
  if (!media || typeof media !== 'object') return;
  if (media.audio instanceof Uint8Array) media.audio.fill(0);
  media.audio = null; media.wav_base64 = null; media.transcript = null; media.text = null;
};
function validWav(audio) {
  if (!(audio instanceof Uint8Array) || audio.length <= 44 || audio.length > 4320044 || audio.length % 2) return false;
  const view = new DataView(audio.buffer, audio.byteOffset, audio.byteLength);
  const ascii = (start, end) => String.fromCharCode(...audio.subarray(start, end));
  return ascii(0, 4) === 'RIFF' && ascii(8, 16) === 'WAVEfmt '
    && view.getUint32(4, true) === audio.length - 8 && view.getUint32(16, true) === 16
    && view.getUint16(20, true) === 1 && view.getUint16(22, true) === 1
    && view.getUint32(24, true) === 24000 && view.getUint32(28, true) === 48000
    && view.getUint16(32, true) === 2 && view.getUint16(34, true) === 16
    && ascii(36, 40) === 'data' && view.getUint32(40, true) === audio.length - 44;
}

class ContinuousVoice {
  constructor({adapter, speechContract, speechWords, id, now = () => performance.now(),
    setTimer = setTimeout, clearTimer = clearTimeout, notify = () => {}, maxTurns = 2}) {
    if (typeof speechContract !== 'function' || typeof speechWords !== 'function' || typeof id !== 'function')
      throw Error('Canonical guards and identity factory are required');
    if (!Number.isInteger(maxTurns) || maxTurns < 2 || maxTurns > 8) throw Error('Turn allowance must be 2..8');
    Object.assign(this, {adapter, speechContract, speechWords, id, now, setTimer, clearTimer, notify, maxTurns});
    this.epoch = id(); this.generation = 0; this.state = 'idle'; this.attempts = 0;
    this.document = null; this.accepted = null; this.active = null; this.capture = null;
    this.media = null; this.player = null; this.partial = ''; this.timer = null;
    this.sessionDeadline = null; this.deadline = null; this.lease = null;
    this.seenTranscripts = new Set();
    this.counts = Object.fromEntries(['starts', 'submitted', 'released', 'played', 'completed',
      'withheld', 'stale', 'cancelled', 'erased'].map(k => [k, 0]));
  }
  context() { return {epoch: this.epoch, generation: this.generation}; }
  _emit() { try { this.notify({state: this.state}); } catch {} } // No visitor content in operational events.
  _current(ticket) { return same(ticket, this.active, BASE) && identity(ticket, this.context()) && !this.abort?.signal.aborted
    && this.now() < this.deadline && this.now() < this.sessionDeadline; }
  _captureCurrent(lease) { return same(lease, this.lease, ['epoch', 'generation', 'capture_id']) && identity(lease, this.context()) && this.state === 'listening'; }
  _arm() {
    if (this.timer !== null) this.clearTimer(this.timer);
    this.timer = null;
    if (['idle', 'paused', 'exhausted', 'blocked'].includes(this.state)) return;
    this.timer = this.setTimer(() => { this.timer = null; this.tick(); },
      Math.max(0, Math.min(this.deadline, this.sessionDeadline) - this.now()));
  }
  tick() {
    if (!['idle', 'paused', 'exhausted', 'blocked'].includes(this.state)
        && (this.now() >= this.deadline || this.now() >= this.sessionDeadline)) {
      this.counts.withheld++; this._invalidate('paused'); return true;
    }
    return false;
  }
  _closeCapture() {
    const handle = this.capture; this.capture = null; this.lease = null; this.partial = '';
    try { handle?.close(); } catch { /* Local invalidation still prevents release. */ }
  }
  _invalidate(state) {
    // Advance before touching resources, so synchronous cancel callbacks are stale.
    this.generation++; this.state = state; this.abort?.abort();
    this._closeCapture();
    const player = this.player; this.player = null;
    try { player?.cancel(); } catch { /* Adapter must provide real cancellation. */ }
    wipe(this.media); this.media = null; this.active = null;
    this._arm(); this.counts.cancelled++;
    // Best-effort transport cancellation is not provider deletion or an acknowledgement.
    try { Promise.resolve(this.adapter.invalidate?.(this.context(), state)).catch(() => {}); } catch {}
    this._emit();
  }
  async start() {
    if (this.state !== 'idle') return false;
    if (typeof this.adapter?.verifyFinal !== 'function' || typeof this.adapter?.settleEcho !== 'function'
        || typeof this.adapter?.control !== 'function' || typeof this.adapter?.complete !== 'function') {
      this.state = 'blocked'; this._emit(); return false;
    }
    this.generation++; this.sessionDeadline = this.now() + 180000;
    this.counts.starts++; return this._listen();
  }
  async resume() {
    if (this.state !== 'paused' || this.attempts >= this.maxTurns || this.now() >= this.sessionDeadline) return false;
    this.generation++; return this._listen(); // Only an explicit UI Resume calls this.
  }
  async _listen() {
    if (this.attempts >= this.maxTurns || this.now() >= this.sessionDeadline) {
      this._invalidate('exhausted'); return false;
    }
    this.abort = new AbortController();
    const signal = this.abort.signal, context = this.context();
    this.state = 'settling'; this.deadline = this.now() + 5000; this._arm(); this._emit();
    try {
      const acknowledged = await this.adapter.control('listen', context, signal);
      this.tick();
      if (!identity(context, this.context()) || signal.aborted) return false;
      if (!identity(acknowledged, context)) throw Error('Conversation control not acknowledged');
      // Half duplex: no capture while research/render/playback is active. Real acoustic
      // settling must be proven by the adapter; a quiet timer alone is not evidence.
      const settled = await this.adapter.settleEcho(context, signal);
      this.tick();
      if (!identity(context, this.context()) || signal.aborted) return false;
      if (settled !== true) { this.counts.withheld++; this._invalidate('paused'); return false; }
      this.lease = {...context, capture_id: this.id()}; const lease = this.lease;
      this.state = 'listening'; this.deadline = this.now() + 30000; this._arm(); this._emit();
      const handle = await this.adapter.openCapture(lease, {
        delta: event => this.inputDelta(event, lease), final: event => this.inputFinal(event, lease),
      }, signal);
      this.tick();
      if (!this._captureCurrent(lease) || signal.aborted) { handle?.close(); return false; }
      if (!handle || typeof handle.close !== 'function') throw Error('Capture cancellation unavailable');
      this.capture = handle; return true;
    } catch {
      if (identity(context, this.context()) && !signal.aborted) { this.counts.withheld++; this._invalidate('paused'); }
      return false;
    }
  }
  inputDelta(event, lease) {
    this.tick();
    if (!this._captureCurrent(lease)) { this.counts.stale++; return false; }
    if (!identity(event, lease) || event.capture_id !== lease.capture_id || typeof event.text !== 'string') return false;
    this.partial = event.text.slice(0, 2000); // Local preview only; never a request.
    return true;
  }
  inputFinal(event, lease) {
    this.tick();
    if (!this._captureCurrent(lease)) { this.counts.stale++; return false; }
    // This is an APPLICATION event, not a fabricated GPT-Live transcript-done event.
    if (!identity(event, lease) || event.capture_id !== lease.capture_id || !textId(event.transcript_id)
        || this.seenTranscripts.has(event.transcript_id)
        || typeof event.text !== 'string' || !event.text.trim() || event.text.length > 2000) return false;
    let final = false;
    try { final = this.adapter.verifyFinal(event, lease) === true; } catch {}
    if (!final) { this.counts.withheld++; return false; }
    this.seenTranscripts.add(event.transcript_id);
    const question = event.text;
    this._closeCapture();
    this.attempts++; this.counts.submitted++;
    const ticket = {...this.context(), turn_id: this.id(), transcript_id: event.transcript_id, request_id: this.id()};
    this.active = ticket; this.state = 'researching'; this.deadline = this.now() + 75000;
    this._arm(); this._emit();
    this.task = this._turn(ticket, question, event.finality, this.abort.signal);
    return true;
  }
  async _turn(ticket, question, finality, signal) {
    let media = null;
    try {
      const release = await this.adapter.ask({ticket, question, finality}, signal);
      this.tick();
      if (!this._current(ticket)) { this.counts.stale++; return; }
      const contract = this.speechContract(release?.result), bound = release?.ticket;
      if (!contract || contract.request_id !== ticket.request_id || !same(bound, ticket, BASE)
          || !RELEASE.slice(BASE.length).every(k => textId(bound[k]))
          || new Set(RELEASE.slice(BASE.length).map(k => bound[k])).size !== 3)
        throw Error('Release withheld');
      this.active = {...bound};
      this.accepted = {ticket: {...bound}, text: contract.text, language: contract.language};
      this.counts.released++; this.state = 'rendering'; this._emit();
      // Identity only: no question or unchecked model draft is given to speech.
      media = await this.adapter.render({...bound}, signal);
      this.tick();
      if (!this._current(bound)) { wipe(media); this.counts.stale++; return; }
      const report = media?.report;
      if (!same(media?.ticket, bound, RELEASE) || media?.request_id !== contract.request_id
          || media?.text !== contract.text || media?.language !== contract.language
          || typeof media?.transcript !== 'string' || this.speechWords(media.transcript) !== this.speechWords(contract.text)
          || report?.acknowledged !== true || report?.transcript_matches !== true || report?.invalid_output !== false
          || report?.final_usage_confirmed !== true || report?.close_reason !== 'close_requested'
          || typeof media?.usage?.seconds !== 'number' || !Number.isFinite(media.usage.seconds) || media.usage.seconds < 0
          || !validWav(media.audio)) throw Error('Audio withheld');
      if (!same(this.accepted?.ticket, bound, RELEASE) || this.accepted.text !== contract.text) throw Error('Display changed');
      this.media = media; this.state = 'playing_pending'; this._emit();
      const handle = this.adapter.play(media, {...bound}, {
        started: () => {
          this.tick();
          if (this._current(bound) && this.state === 'playing_pending') {
            this.state = 'speaking'; this.counts.played++; this._emit();
          }
        },
        ended: () => { this._ended(bound); },
        failed: () => { if (this._current(bound) && ['playing_pending', 'speaking'].includes(this.state)) { this.counts.withheld++; this._invalidate('paused'); } },
      }, signal);
      if (!handle || typeof handle.cancel !== 'function') throw Error('Playback cancellation unavailable');
      if (!this._current(bound) || !['playing_pending', 'speaking'].includes(this.state)) { handle.cancel(); return; }
      this.player = handle;
    } catch {
      wipe(media);
      if (this._current(ticket)) { this.counts.withheld++; this._invalidate('paused'); }
    }
  }
  _ended(ticket) {
    this.tick();
    if (!this._current(ticket) || this.state !== 'speaking') { this.counts.stale++; return false; }
    const player = this.player; this.player = null;
    wipe(this.media); this.media = null; this.state = 'finishing'; this._emit();
    try { player?.cancel(); } catch {} // Release player resources/object URLs after normal end too.
    this.task = this._finish(ticket);
    return true;
  }
  async _finish(ticket) {
    try {
      const acknowledged = await this.adapter.complete({...ticket}, this.abort.signal);
      this.tick();
      if (!this._current(ticket)) return;
      if (acknowledged !== true) throw Error('Playback completion not acknowledged');
      this.active = null; this.abort.abort(); this.counts.completed++;
      await this._listen(); // Next turn automatically, without confirm or manual Play.
    } catch {
      if (this._current(ticket)) { this.counts.withheld++; this._invalidate('paused'); }
    }
  }
  stop() { this._invalidate('paused'); } // Document and accepted text intentionally survive.
  async interrupt() {
    if (!['researching', 'rendering', 'playing_pending', 'speaking'].includes(this.state)) return false;
    this._invalidate('paused'); return this.resume(); // Deliberate touch interruption only.
  }
  erase() {
    const document = this.document;
    this._invalidate('idle'); this.document = this.accepted = null;
    try { this.adapter.clearDocument?.(document); } catch {} // Intake owner clears bytes/previews.
    this.epoch = this.id(); this.attempts = 0; this.sessionDeadline = this.deadline = null;
    this.seenTranscripts.clear();
    this.counts.erased++; this._emit();
    try { Promise.resolve(this.adapter.erase?.(this.context())).catch(() => {}); } catch {}
  }
  metrics() { return {...this.counts}; }
}
module.exports = {ContinuousVoice, BASE, RELEASE, wipe, validWav};
