'use strict';
// No device access, network listener, wake detector, or sensor simulation in this module.
class OracleInteraction {
  constructor({ onChange = () => {}, onIntent = () => {}, onReset = async () => {}, now = () => performance.now(), setTimer = (...args) => setTimeout(...args), clearTimer = (...args) => clearTimeout(...args), presenceDwellMs = 500, invitationReadMs = 200, presenceLeaseMs = 3000, resetTimeoutMs = 5000 } = {}) {
    this.onChange = onChange; this.onIntent = onIntent; this.onReset = onReset; this.now = now;
    this.setTimer = setTimer; this.clearTimer = clearTimer; this.presenceDwellMs = presenceDwellMs; this.resetTimeoutMs = resetTimeoutMs; this.invitationReadMs = invitationReadMs; this.presenceLeaseMs = presenceLeaseMs; this.accepted = false; this.invitedAt = null;
    this.state = 'idle'; this.generation = 0; this.turn = 0; this.present = null;
    this.voiceReady = false; this.presenceReady = false; this.waveReady = false; this.wakeReady = false; this.resetPending = null;
    this.publish();
  }
  token() { return Object.freeze({ generation: this.generation, turn: this.turn }); }
  valid(token) { return token?.generation === this.generation && token.turn === this.turn; }
  snapshot() { return Object.freeze({ state: this.state, generation: this.generation, turn: this.turn, presence: this.present, voiceReady: this.voiceReady, presenceReady: this.presenceReady, waveReady: this.waveReady, wakeReady: this.wakeReady }); }
  publish() { this.onChange(this.snapshot()); }
  move(state) { this.state = state; if (state === 'invitation') this.invitedAt = this.now(); this.publish(); }
  configure({ voiceReady = this.voiceReady, presenceReady = this.presenceReady, waveReady = this.waveReady, wakeReady = this.wakeReady } = {}) {
    this.voiceReady = voiceReady === true; this.presenceReady = presenceReady === true;
    this.waveReady = waveReady === true; this.wakeReady = wakeReady === true;
    if (!this.presenceReady) { this.clearTimer(this.presenceTimer); this.clearTimer(this.presenceLease); this.present = null; if (['presence','invitation'].includes(this.state)) this.state = 'idle'; }
    this.publish();
  }
  presence(detected) {
    if (!this.presenceReady || typeof detected !== 'boolean' || this.state === 'reset') return false;
    this.present = detected;
    this.clearTimer(this.presenceLease);
    if (detected) {
      const generation = this.generation;
      this.presenceLease = this.setTimer(() => { if (generation !== this.generation) return; this.present = null; this.clearTimer(this.presenceTimer); if (['presence','invitation'].includes(this.state)) this.move('idle'); else this.publish(); }, this.presenceLeaseMs);
    }
    if (!detected) this.clearTimer(this.presenceTimer);
    if (detected && this.state === 'idle') {
      this.move('presence'); const generation = this.generation;
      this.presenceTimer = this.setTimer(() => { if (generation === this.generation && this.state === 'presence' && this.present === true && this.presenceReady) this.move('invitation'); }, this.presenceDwellMs);
    } else if (!detected && ['presence','invitation'].includes(this.state)) this.move('idle');
    else this.publish();
    return true;
  }
  intent(source, observedAt = this.now()) {
    const sensor = source === 'camera_wave' || source === 'spoken_initiation';
    const fallback = ['accessible_control','presenter_key','presenter_click'].includes(source);
    if (!this.voiceReady || this.state === 'reset' || (!sensor && !fallback)) return false;
    if (sensor && (!Number.isFinite(observedAt) || this.invitedAt === null || observedAt < this.invitedAt + this.invitationReadMs || this.state !== 'invitation' || this.present !== true || !this.presenceReady || (source === 'camera_wave' ? !this.waveReady : !this.wakeReady))) return false;
    if (fallback && !['idle','presence','invitation','conversation','answer_ready'].includes(this.state)) return false;
    this.clearTimer(this.presenceTimer); this.turn++; this.accepted = false; this.move('intent');
    const token = this.token();
    Promise.resolve().then(() => { if (this.valid(token) && this.state === 'intent') return this.onIntent(token); }).catch(() => this.signal('capture_failed', token));
    return true;
  }
  beginThinking() { if (this.state === 'reset') return null; this.clearTimer(this.presenceTimer); this.turn++; this.accepted = false; this.move('thinking'); return this.token(); }
  signal(type, token) {
    if (!this.valid(token) || this.state === 'reset') return false;
    const routes = {
      capture_ready: [['intent'], 'listening'], transcript_review: [['listening'], 'review'],
      capture_failed: [['intent','listening','review'], 'conversation'],
      answer_accepted: [['thinking'], 'answer_ready'], answer_withheld: [['thinking'], 'conversation'],
      speech_preparing: [['answer_ready'], 'preparing_speech'],
      speech_ready: [['preparing_speech'], 'answer_ready'],
      playback_started: [['preparing_speech','answer_ready'], 'speaking'],
      playback_finished: [['speaking'], 'answer_ready'], speech_held: [['preparing_speech','speaking'], this.accepted ? 'answer_ready' : 'conversation']
    };
    const route = routes[type]; if (!route || !route[0].includes(this.state)) return false;
    if (['speech_preparing','speech_ready','playback_started'].includes(type) && !this.accepted) return false;
    if (type === 'answer_accepted') this.accepted = true;
    if (type === 'answer_withheld') this.accepted = false;
    this.move(route[1]); return true;
  }
  departure() {
    if (!this.presenceReady || this.present !== false) return false;
    this.reset('departure'); return true;
  }
  reset(reason = 'accessible_control') {
    if (this.resetPending) return this.resetPending;
    this.clearTimer(this.presenceTimer); this.clearTimer(this.presenceLease); this.accepted = false; this.generation++; this.turn++; this.present = null; this.move('reset');
    let finish, timer; const generation = this.generation;
    const result = new Promise(resolve => { finish = resolve; }); this.resetPending = result;
    // Invoke cleanup synchronously: stop tracks/playback before awaiting provider teardown.
    let cleanup; try { cleanup = this.onReset({ reason, generation }); } catch { cleanup = Promise.reject(Error('cleanup')); }
    const timeout = new Promise((_, reject) => { timer = this.setTimer(() => reject(Error('cleanup_timeout')), this.resetTimeoutMs); });
    Promise.race([Promise.resolve(cleanup), timeout]).then(() => {
      this.clearTimer(timer); if (generation === this.generation) { this.resetPending = null; this.move('idle'); } finish(true);
    }, () => { this.clearTimer(timer); this.resetPending = null; this.publish(); finish(false); });
    // Failure deliberately remains reset/blocked; no unverified cleanup means no re-arm.
    return result;
  }
}

class OracleSensorAdapter {
  constructor(interaction, { sessionId, producerMonotonicMs, sources, capabilities = {}, now = () => performance.now(), maxAgeMs = 2000 } = {}) {
    if (typeof sessionId !== 'string' || sessionId.length < 8 || sessionId.length > 128 || !Number.isFinite(producerMonotonicMs) || producerMonotonicMs < 0 || !Array.isArray(sources) || !sources.length || sources.some(s => !['camera','camera_wave','spoken_initiation','presenter_key','presenter_click'].includes(s))) throw Error('Invalid sensor registration');
    this.interaction = interaction; this.sessionId = sessionId; this.sources = new Set(sources); this.sequence = -1; this.closed = false;
    this.now = now; this.anchor = now() - producerMonotonicMs; this.maxAgeMs = maxAgeMs;
    this.capabilities = { presence: capabilities.presence === true, wave: capabilities.wave === true, localWake: capabilities.localWake === true };
    interaction.configure({ presenceReady: this.capabilities.presence, waveReady: this.capabilities.wave, wakeReady: this.capabilities.localWake });
  }
  accept(event) {
    if (this.closed || !event || typeof event.type !== 'string' || typeof event.source !== 'string' || event.schema !== 'open-oracle-input/v1' || event.synthetic !== false || event.session_id !== this.sessionId || !this.sources.has(event.source) || !Number.isSafeInteger(event.sequence) || event.sequence < 0 || event.sequence <= this.sequence || !Number.isFinite(event.monotonic_ms) || event.monotonic_ms < 0) return false;
    const age = this.now() - (this.anchor + event.monotonic_ms);
    if (age < -250 || age > this.maxAgeMs) { this.close(); return false; }
    const pair = event.type + ':' + event.source;
    const known = ['presence_detected:camera','presence_lost:camera','departure_confirmed:camera','start_requested:camera_wave','start_requested:spoken_initiation','start_requested:presenter_key','start_requested:presenter_click','reset_requested:presenter_key','reset_requested:presenter_click','error:camera','stopped:camera'];
    if (!known.includes(pair)) return false;
    this.sequence = event.sequence; // Valid observed event is consumed even when the current state declines it.
    if (event.type === 'error' || event.type === 'stopped') { this.close(); return true; }
    if (event.type === 'presence_detected') return this.capabilities.presence && this.interaction.presence(true);
    if (event.type === 'presence_lost') return this.capabilities.presence && this.interaction.presence(false);
    if (event.type === 'departure_confirmed') return this.capabilities.presence && this.interaction.departure();
    if (event.type === 'reset_requested') { this.interaction.reset('presenter'); return true; }
    if (event.source === 'camera_wave' && !this.capabilities.wave) return false;
    if (event.source === 'spoken_initiation' && !this.capabilities.localWake) return false;
    return event.type === 'start_requested' && this.interaction.intent(event.source, this.anchor + event.monotonic_ms);
  }
  close() { if (this.closed) return; this.closed = true; this.interaction.configure({ presenceReady: false, waveReady: false, wakeReady: false }); }
}
if (typeof module !== 'undefined') module.exports = { OracleInteraction, OracleSensorAdapter };
if (typeof window !== 'undefined') { window.OracleInteraction = OracleInteraction; window.OracleSensorAdapter = OracleSensorAdapter; }
