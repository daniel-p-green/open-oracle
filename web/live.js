'use strict';
// Only the remote generated track is buffered in memory. No microphone recording.
// GPT-Live has no transcript-done event: require confirmed session closure.
// Preserve numeric signs, decimal/grouping marks, percent and currency units.
// Ordinary prose punctuation may differ; numeric meaning must never be erased.
const speechWords = value => (String(value).normalize('NFKC').toLowerCase().replace(/[’‘]/g, "'")
  .match(/[+\-−]?\s*\p{N}+(?:[.,]\p{N}+)*|[.,]\p{N}+|[%‰$€£¥]|[\p{L}\p{N}']+/gu) || [])
  .map(token => token.replace(/\s/g, '').replace(/−/g, '-')).join(' ');
function eraseIntent(value) {
  const normalized = String(value).normalize('NFKD').replace(/\p{M}/gu, '').toLowerCase().replace(/[.!?,¡¿]/g, '').replace(/\s+/g, ' ').trim();
  return /^(?:please )?(?:erase|delete|clear) (?:this|my|the) session$|^(?:por favor )?(?:borra|borrar|elimina) (?:esta|mi) sesion$|^(?:efface|supprime) (?:cette|ma) session$|^(?:losche) (?:diese|meine) sitzung$|^(?:apague|apagar) (?:esta|minha) sessao$/.test(normalized);
}
// Retain billing/closure proof only, never provider identifiers or session snapshots.
function closedUsageMetadata(event) {
  const reasons = ['close_requested', 'expired', 'content', 'remote_hangup', 'connection_lost'];
  const metadata = { type: 'session.closed', reason: reasons.includes(event?.reason) ? event.reason : 'unknown' };
  if (typeof event?.usage?.seconds === 'number' && Number.isFinite(event.usage.seconds) && event.usage.seconds >= 0) metadata.usage = { seconds: event.usage.seconds };
  return metadata;
}
function speechContract(result) {
  const speech = result?.speech;
  if (result?.status !== 'answered' || result.review?.execution !== 'real_api' || result.review.status !== 'accepted' || result.fact_validation?.status !== 'supported' || result.language !== 'en' || result.translation_status !== 'not_requested') return null;
  if (!speech || speech.request_id !== result.request_id || speech.text !== result.answer || speech.language !== 'en' || !Array.isArray(speech.evidence_bindings) || !speech.evidence_bindings.length || speech.text.length > 1800) return null;
  if (!speech.evidence_bindings.every(b => result.evidence?.some(e => e.id === b.id && e.sha256 === b.sha256 && e.text === b.text && e.contest_id === result.contest?.id))) return null;
  return structuredClone(speech);
}
// Sequencing only: host owns tickets, capture, evidence, speech and playback.
async function checkedQuestionFlow({ current, finishInput, requestAnswer, prepare, play, canHear }) {
  if (!current()) return 'cancelled';
  const input = await finishInput();
  if (!current()) return 'cancelled';
  if (!input || input.final !== true || typeof input.text !== 'string' || !input.text.trim()) return 'input_held';
  const result = await requestAnswer(input.text);
  if (!current()) return 'cancelled';
  if (!speechContract(result)) return 'answer_held';
  const ready = await prepare(result);
  if (!current()) return 'cancelled';
  if (ready !== true || !canHear()) return 'audio_held';
  try { await play(); return current() ? 'playing' : 'cancelled'; }
  catch { return current() && canHear() ? 'hear_fallback' : 'audio_held'; }
}

// Bound permission and browser negotiation even when an implementation never settles.
// A late permission grant must release its tracks after Stop, Erase or timeout.
function boundedLiveOperation(operation, { timeoutMs, signal, message, onLateResolve } = {}) {
  return new Promise((resolve, reject) => {
    let done = false, timer;
    const finish = (callback, value) => {
      if (done) return;
      done = true; clearTimeout(timer); signal?.removeEventListener('abort', abort);
      callback(value);
    };
    const abort = () => finish(reject, new DOMException('Voice start stopped.', 'AbortError'));
    Promise.resolve(operation).then(value => {
      if (done) { onLateResolve?.(value); return; }
      finish(resolve, value);
    }, error => finish(reject, error));
    if (signal?.aborted) { abort(); return; }
    signal?.addEventListener('abort', abort, { once: true });
    timer = setTimeout(() => finish(reject, new Error(message)), timeoutMs);
  });
}

async function trimRemoteAudio(blob) {
  const context = new OfflineAudioContext(1, 1, 24000);
  try {
    const audio = await Promise.race([context.decodeAudioData(await blob.arrayBuffer()), new Promise((_, reject) => setTimeout(() => reject(new Error('Audio decoding timed out')), 4000))]);
    if (audio.duration > 90 || audio.numberOfChannels < 1) throw new Error('Invalid buffered audio');
    const channel = audio.getChannelData(0), threshold = 0.0005;
    let first = 0, last = channel.length - 1;
    while (first < channel.length && Math.abs(channel[first]) < threshold) first++;
    while (last > first && Math.abs(channel[last]) < threshold) last--;
    if (first >= last) throw new Error('No generated speech in the buffer');
    const padding = Math.round(audio.sampleRate * 0.15);
    first = Math.max(0, first - padding); last = Math.min(channel.length - 1, last + padding);
    const count = last - first + 1, wav = new ArrayBuffer(44 + count * 2), view = new DataView(wav);
    const text = (offset, value) => { for (let i = 0; i < value.length; i++) view.setUint8(offset + i, value.charCodeAt(i)); };
    text(0, 'RIFF'); view.setUint32(4, 36 + count * 2, true); text(8, 'WAVE'); text(12, 'fmt ');
    view.setUint32(16, 16, true); view.setUint16(20, 1, true); view.setUint16(22, 1, true);
    view.setUint32(24, audio.sampleRate, true); view.setUint32(28, audio.sampleRate * 2, true); view.setUint16(32, 2, true); view.setUint16(34, 16, true);
    text(36, 'data'); view.setUint32(40, count * 2, true);
    for (let i = 0; i < count; i++) { const value = Math.max(-1, Math.min(1, channel[first + i])); view.setInt16(44 + i * 2, Math.round(value * (value < 0 ? 32768 : 32767)), true); }
    return { blob: new Blob([wav], { type: 'audio/wav' }), duration_ms: Math.round(count / audio.sampleRate * 1000), trimmed_silence_ms: Math.round((audio.length - count) / audio.sampleRate * 1000) };
  } finally { /* Offline decoding creates no speaker or microphone stream. */ }
}
function createGeneratedSilence({Track=globalThis.MediaStreamTrackGenerator,Frame=globalThis.AudioData,Stream=globalThis.MediaStream,setTimer=globalThis.setTimeout.bind(globalThis),clearTimer=globalThis.clearTimeout.bind(globalThis)}={}){
 if(typeof Track!=='function'||typeof Frame!=='function'||typeof Stream!=='function')throw Error('Voice playback is unavailable in this browser. Open this page in Chrome or ask for station help.');
 const track=new Track({kind:'audio'}),writer=track.writable.getWriter(),stream=new Stream([track]);
 let active=true,frames=0,timer=null,wake=null,failure=null;
 const task=(async()=>{try{while(active){const frame=new Frame({format:'f32-planar',sampleRate:48000,numberOfFrames:960,numberOfChannels:1,timestamp:Math.round(frames/48000*1e6),data:new Float32Array(960)});try{await writer.write(frame);frames+=960;}finally{frame.close();}if(active)await new Promise(resolve=>{wake=resolve;timer=setTimer(()=>{timer=null;wake=null;resolve()},20)})}}catch(error){failure=error.name;active=false;track.stop();}finally{try{await writer.close()}catch{}}})();
 return{track,stream,stats:()=>({source:'generated_pcm_zero_frames',hardware:false,frames_written:frames,sample_rate:48000,active,track_state:track.readyState,failure}),stop(){active=false;if(timer!==null)clearTimer(timer);wake?.();wake=null;timer=null;track.stop();},finished:task};
}
class OpenOracleLive {
  constructor(notify, currentDisplay = () => null) {
    this.waitForOperation = boundedLiveOperation; this.startupPhase = 'idle';
    this.createSilence = createGeneratedSilence; this.finalizeAudio = trimRemoteAudio; this.notify = notify; this.currentDisplay = currentDisplay; this.generation = 0; this.playbackToken = 0; this.started = false;
    this.transcript = ''; this.fragments = []; this.delegations = new Set(); this.pendingDelegation = null;
    this.outputTranscript = ''; this.outputEvents = new Set(); this.chunks = []; this.bufferBytes = 0; this.prepared = null; this.ready = null;
  }
  send(command) {
    if (!this.started || this.channel?.readyState !== 'open') return false;
    try { this.channel.send(JSON.stringify({ event_id: crypto.randomUUID(), ...command })); return true; } catch { return false; }
  }
  validDisplay(contract) {
    const display = this.currentDisplay();
    return display?.request_id === contract.request_id && display?.text === contract.text && display?.language === contract.language;
  }
  handle(event, generation) {
    if (event?.type === 'session.closed' && generation === this.closingGeneration && generation !== this.generation) { this.closedEvent = closedUsageMetadata(event); this.finalUsageConfirmed = Boolean(this.closedEvent.usage); this.finishClose?.(); return; }
    if (generation !== this.generation || !event || typeof event !== 'object') return;
    if (event.type === 'session.started') {
      if (this.started) return;
      this.started = true; this.startupPhase = 'listening'; clearTimeout(this.startupTimer);
      if (this.timings) this.timings.connect_ms = Math.round(performance.now() - this.timings.connection_started);
      this.stream?.getAudioTracks().forEach(t => { t.enabled = true; });
      this.notify({ type: this.stream ? 'listening' : 'connected', text: this.stream ? 'Say one question, then review the transcript.' : 'Connected. Preparing the displayed answer.' });
      this.resolveStarted?.();
      if (this.stream) this.noInputTimer = setTimeout(() => {
        if (generation !== this.generation || this.transcript.trim() || this.pendingDelegation) return;
        this.inputFailure = 'I did not hear a question. Check your microphone, then choose Talk again.';
        this.notify({type:'error', text:'I did not hear a question. Check your microphone, then choose Talk again.'});
        this.close();
      }, 20000);
    } else if (event.type === 'session.input_transcript.delta') {
      if (typeof event.delta === 'string' && eraseIntent(this.transcript + event.delta)) {
        this.cancel(); this.notify({ type: 'erase_requested', text: 'Clearing this session locally.' }); return;
      }
      if (typeof event.delta !== 'string' || this.prepared || this.pendingDelegation || this.inputFrozen) return;
      this.fragments.push({ delta: event.delta, start_ms: event.start_ms, end_ms: event.end_ms });
      this.transcript += event.delta;
      if (this.transcript.trim()) clearTimeout(this.noInputTimer);
      if (this.transcript.length > 2000) { this.transcript = this.transcript.slice(0,2000); this.inputFrozen = true; this.mute(); this.stream?.getTracks().forEach(t => t.stop()); this.notify({ type: 'transcript', text: this.transcript }); this.notify({ type: 'review', text: 'Microphone stopped at the question length limit. Review or shorten the transcript.' }); return; }
      this.notify({ type: 'transcript', text: this.transcript });
    } else if (event.type === 'session.delegation.created') {
      const delegation = event.delegation;
      if (delegation?.target !== 'client' || typeof delegation.id !== 'string' || this.delegations.has(delegation.id)) return;
      this.delegations.add(delegation.id); this.pendingDelegation = delegation.id;
      this.mute(); this.stream?.getTracks().forEach(t => t.stop());
      this.notify({ type: 'review', text: 'Microphone stopped. Check the words we heard, then choose Ask.' });
    } else if (event.type === 'session.output_transcript.delta') {
      if (typeof event.delta !== 'string' || typeof event.event_id !== 'string' || this.outputEvents.has(event.event_id)) { this.invalidOutput = true; return; }
      this.outputEvents.add(event.event_id); this.outputTranscript += event.delta;
      if (this.outputTranscript.length > 2400) { this.invalidOutput = true; this.close(); return; }
      this.notify({ type: 'buffering', text: 'Preparing speech. Nothing plays until it matches the displayed answer.' });
      clearTimeout(this.outputTimer);
      // Silence only schedules closure; it never establishes completion/acceptance.
      if (this.prepared) this.outputTimer = setTimeout(() => this.close({ release: true }), 1500);
    } else if (event.type === 'session.commentary.appended' && event.client_event_id === this.commentaryId) {
      this.commentaryAcknowledged = true;
    } else if (event.type === 'session.closed') {
      this.closedEvent = closedUsageMetadata(event); this.finalUsageConfirmed = Boolean(this.closedEvent.usage); this.finishClose?.();
      if (!this.closePromise) this.close({ release: true });
    } else if (event.type === 'error') {
      this.invalidOutput = true; this.notify({ type: 'error', text: 'Voice could not finish. Your text and sources remain available.' }); this.close();
    }
  }
  async start({ microphone = true } = {}) {
    if (microphone && (!globalThis.isSecureContext || !navigator.mediaDevices?.getUserMedia || typeof RTCPeerConnection !== 'function')) throw new Error('This browser cannot use the microphone here. Open this page in Chrome or Safari, or ask for station help.');
    if (this.peer || this.closePromise || this.starting || this.wsAbort) throw new Error('Stop the current voice session first.');
    this.cancelPlayback();
    this.timings = { connection_started: performance.now() };
    const generation = ++this.generation; this.starting = true; this.startGeneration = generation; this.closing = false; this.inputFrozen = false; this.sessionAbort = new AbortController();
    this.transcript = ''; this.fragments = []; this.pendingDelegation = null; this.delegations.clear(); this.finalUsageConfirmed = false; this.inputFailure = null;
    this.lastValidation = null; this.outputTranscript = ''; this.outputEvents.clear(); this.chunks = []; this.bufferBytes = 0; this.invalidOutput = false; this.prepared = null; this.closedEvent = null; this.commentaryAcknowledged = false;
    this.notify({ type: 'connecting', text: microphone ? 'Allow the microphone to speak one question.' : 'Connecting voice for the displayed answer…' });
    try {
      if (microphone) {
        this.startupPhase = 'permission';
        const stream = await this.waitForOperation(navigator.mediaDevices.getUserMedia({ audio: true }), {
          timeoutMs: 12000, signal: this.sessionAbort.signal,
          message: 'Microphone permission did not finish. Allow it in your browser, then choose Talk again.',
          onLateResolve: stream => stream.getTracks().forEach(track => track.stop())
        });
        if (generation !== this.generation) { stream.getTracks().forEach(t => t.stop()); return; }
        this.stream = stream; stream.getAudioTracks().forEach(t => { t.enabled = false; });
      }
      this.peer = new RTCPeerConnection();
      if (this.stream) this.stream.getTracks().forEach(track => { this.sender = this.peer.addTrack(track, this.stream); });
      else {
        // GPT-Live context/speech requires an advancing upstream media timeline.
        // Send generated PCM zeros; this never acquires a microphone or speaker.
        this.silence = this.createSilence();
        this.sender = this.peer.addTrack(this.silence.track, this.silence.stream);
      }
      this.peer.ontrack = event => {
        // Never attach incoming media to a player. Capture this remote output track only.
        if (generation !== this.generation || this.recorder) return;
        const mimeType = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4'].find(t => MediaRecorder.isTypeSupported(t));
        if (!mimeType) { this.invalidOutput = true; return; }
        this.recorder = new MediaRecorder(new MediaStream([event.track]), { mimeType });
        this.recorder.ondataavailable = data => {
          if (generation !== this.generation || this.invalidOutput || !data.data.size) return;
          this.bufferBytes += data.data.size;
          if (this.bufferBytes > 8 * 1024 * 1024) { this.invalidOutput = true; this.chunks = []; return; }
          this.chunks.push(data.data);
        };
        this.recorder.onerror = () => { this.invalidOutput = true; };
        this.recorder.start(250);
      };
      this.channel = this.peer.createDataChannel('oai-events');
      this.channel.onmessage = message => { try { this.handle(JSON.parse(message.data), generation); } catch { this.invalidOutput = true; } };
      const started = new Promise((resolve, reject) => {
        this.resolveStarted = resolve; this.rejectStarted = reject;
        this.startupTimer = setTimeout(() => reject(new Error('Voice did not connect. Choose Talk again or ask for station help.')), 30000);
      });
      // Mark rejected startup as handled even if SDP negotiation fails first.
      started.catch(() => {});
      this.startupPhase = 'offer';
      const offer = await this.waitForOperation(this.peer.createOffer(), { timeoutMs: 10000, signal: this.sessionAbort.signal, message: 'Voice connection did not finish. Choose Talk again.' });
      if (generation !== this.generation) return;
      await this.waitForOperation(this.peer.setLocalDescription(offer), { timeoutMs: 10000, signal: this.sessionAbort.signal, message: 'Voice connection did not finish. Choose Talk again.' });
      this.startupPhase = 'ice';
      if (generation !== this.generation) return;
      if (this.peer.iceGatheringState !== 'complete') await new Promise((resolve, reject) => {
        const timer = setTimeout(() => reject(new Error('Voice connection timed out. Choose Talk again or ask for station help.')), 10000);
        this.peer.onicegatheringstatechange = () => { if (this.peer?.iceGatheringState === 'complete') { clearTimeout(timer); resolve(); } };
      });
      if (generation !== this.generation) return;
      this.startupPhase = 'provider';
      const response = await fetch('/api/live/session', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ sdp: this.peer.localDescription.sdp }), signal: AbortSignal.any([this.sessionAbort.signal, AbortSignal.timeout(20000)]) });
      const result = await response.json();
      if (generation !== this.generation) return;
      if (Number.isInteger(result.voice_sessions_remaining)) this.notify({ type: 'allowance', remaining: result.voice_sessions_remaining, text: result.voice_sessions_remaining > 0 ? 'Voice is available for another question.' : 'The approved voice allowance is used. This question can finish.' });
      if (!response.ok) { if (response.status === 429 || response.status === 503) this.notify({ type: 'unavailable', text: 'Voice session allowance is unavailable. Ask for station help.' }); throw new Error(result.error || 'Voice could not connect. Choose Talk again or ask for station help.'); }
      if (generation !== this.generation) return;
      this.startupPhase = 'peer';
      await this.waitForOperation(this.peer.setRemoteDescription({ type: 'answer', sdp: result.transport.sdp }), { timeoutMs: 10000, signal: this.sessionAbort.signal, message: 'Voice could not finish connecting. Choose Talk again.' });
      if (!this.started) this.startupPhase = 'session_started';
      await this.waitForOperation(started, { timeoutMs: 10000, signal: this.sessionAbort.signal, message: 'Voice did not start listening. Choose Talk again.' });
      if (generation !== this.generation) return;
      this.startupPhase = 'listening';
      this.limitTimer = setTimeout(() => this.close(), 75000);
    } catch (error) {
      if (generation !== this.generation) return;
      // Cleanup emits stopped before the host catch runs; retain the plain cause.
      const deviceErrors = {
        NotAllowedError: 'Microphone permission was not granted. Allow it in your browser, then choose Talk again.',
        NotFoundError: 'No microphone was found. Connect one, then choose Talk again.',
        NotReadableError: 'The microphone is busy or unavailable. Close other apps using it, then choose Talk again.'
      };
      this.inputFailure = deviceErrors[error.name] || (error.message === 'Microphone permission did not finish. Allow it in your browser, then choose Talk again.' ? error.message : 'Voice could not connect. Choose Talk again.');
      await this.close(); throw error;
    } finally { if (this.startGeneration === generation) this.starting = false; }
  }
  mute({ maintainTimeline = true } = {}) {
    this.stream?.getAudioTracks().forEach(t => { t.enabled = false; });
    // Physical capture ends immediately; only generated silence keeps media time moving.
    if (maintainTimeline && !this.closing && this.sender && this.stream) {
      const stream = this.stream; this.stream = null; stream.getTracks().forEach(t => t.stop());
      const generation = this.generation;
      try {
        this.silence ||= this.createSilence();
        Promise.resolve(this.sender.replaceTrack(this.silence.track)).catch(() => {
          if (generation !== this.generation) return;
          this.invalidOutput = true; this.close();
        });
      } catch { this.invalidOutput = true; queueMicrotask(() => { if (generation === this.generation) this.close(); }); }
    }
    this.send({ type: 'session.input_audio.mute' });
  }
  evidenceContext(result) {
    this.mute(); this.stream?.getTracks().forEach(t => t.stop());
    const contract = speechContract(result);
    if (!contract) { if (this.started) this.close(); return false; }
    if (!this.started || !this.validDisplay(contract) || this.prepared) return false;
    this.prepared = contract; if (this.timings) this.timings.speech_submitted = performance.now(); this.commentaryId = crypto.randomUUID();
    if (!this.send({ type: 'session.commentary.append', event_id: this.commentaryId, delegation_id: this.pendingDelegation,
      content: contract.text })) { this.prepared = null; return false; }
    this.pendingDelegation = null;
    this.notify({ type: 'buffering', text: 'Preparing speech. The full answer is already visible.' });
    return true;
  }
  cancelPlayback() {
    this.playbackToken++; this.ready = null;
    if (this.player) { this.player.pause(); this.player.removeAttribute('src'); this.player.load(); this.player = null; }
    if (this.audioUrl) URL.revokeObjectURL(this.audioUrl); this.audioUrl = null;
  }
  cancel() {
    if (this.wsAbort) { this.wsAbort.abort(); this.generation++; this.wsAbort = null; this.prepared = null; }
    this.cancelPlayback(); this.mute({ maintainTimeline: false }); this.stream?.getTracks().forEach(t => t.stop());
    if (this.starting || this.prepared) { this.prepared = null; this.invalidOutput = true; this.close(); }
  }
  discardVisitor() {
    this.cancel(); this.transcript = ''; this.fragments = []; this.outputTranscript = ''; this.lastValidation = null;
    this.chunks = []; this.bufferBytes = 0; this.pendingDelegation = null; this.delegations.clear();
  }
  async prepareServer(result, sessionId) {
    const contract = speechContract(result);
    if (!contract || !this.validDisplay(contract) || this.peer || this.closePromise || this.wsAbort) throw new Error('Speech requires the current accepted answer and sources.');
    this.cancelPlayback(); const generation = ++this.generation, token = this.playbackToken;
    const abort = new AbortController(); this.wsAbort = abort; this.prepared = contract;
    this.notify({ type: 'buffering', text: 'Preparing speech. The accepted answer is already visible.' });
    try {
      const response = await fetch('/api/live/speech', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Oracle-Session': sessionId }, body: JSON.stringify({ request_id: contract.request_id }), signal: abort.signal });
      if (generation !== this.generation || token !== this.playbackToken) return false;
      const data = await response.json();
      if (generation !== this.generation || token !== this.playbackToken) return false;
      if (Number.isInteger(data.voice_sessions_remaining)) this.notify({ type: 'allowance', remaining: data.voice_sessions_remaining, text: data.voice_sessions_remaining > 0 ? 'Voice is available for another question.' : 'The approved voice allowance is used. This answer can finish.' });
      if (!response.ok || !data.accepted || data.request_id !== contract.request_id || data.text !== contract.text || data.language !== contract.language || speechWords(data.transcript) !== speechWords(contract.text) || data.report?.close_reason !== 'close_requested' || data.report?.final_usage_confirmed !== true || data.report?.acknowledged !== true || data.report?.invalid_output !== false || !Number.isFinite(data.usage?.seconds) || data.usage.seconds < 0 || typeof data.wav_base64 !== 'string' || data.wav_base64.length > 6 * 1024 * 1024) throw new Error('Speech did not match or finish. Read the accepted answer and its sources.');
      const bytes = Uint8Array.from(atob(data.wav_base64), c => c.charCodeAt(0));
      const audio = await this.finalizeAudio(new Blob([bytes], { type: 'audio/wav' }));
      if (generation !== this.generation || token !== this.playbackToken || abort.signal.aborted || !this.validDisplay(contract)) return false;
      this.lastValidation = { request_id: contract.request_id, transport: 'websocket', ...data.report, decode: 'succeeded' };
      this.closedEvent = closedUsageMetadata({ reason: data.report.close_reason, usage: data.usage });
      this.ready = { contract, ...audio, transcript: data.transcript };
      this.notify({ type: 'ready', text: 'Speech matches the displayed answer. Choose Play answer.' });
      return true;
    } catch (error) {
      if (generation === this.generation && !abort.signal.aborted) this.notify({ type: 'held', text: 'Voice did not match or finish. Read the answer; its sources are available.' });
      if (abort.signal.aborted || generation !== this.generation) return false;
      throw error;
    } finally { if (this.wsAbort === abort) this.wsAbort = null; if (this.prepared === contract) this.prepared = null; }
  }
  async play() {
    const ready = this.ready;
    if (!ready || !this.validDisplay(ready.contract)) { this.cancelPlayback(); throw new Error('That answer changed. Prepare speech again.'); }
    if (this.player && !this.player.paused) { this.player.pause(); this.notify({ type: 'paused', request_id: ready.contract.request_id, playing: false, text: 'Playback stopped. The displayed answer remains readable.' }); return; }
    const token = this.playbackToken;
    if (!this.player) {
      this.audioUrl = URL.createObjectURL(ready.blob); this.player = new Audio(this.audioUrl);
      this.player.onplaying = () => { if (token === this.playbackToken && this.validDisplay(ready.contract)) this.notify({ type: 'speaking', request_id: ready.contract.request_id, validated: true, playing: this.player?.paused === false, text: 'Playing the displayed answer.' }); else this.cancelPlayback(); };
      this.player.onended = () => { if (token === this.playbackToken) this.notify({ type: 'finished', request_id: ready.contract.request_id, playing: false, text: 'Playback finished. Sources remain available.' }); };
      this.player.onerror = () => { if (token === this.playbackToken) { this.cancelPlayback(); this.notify({ type: 'error', text: 'Playback failed. Read the answer or inspect its sources.' }); } };
    }
    let timer;
    try {
      await Promise.race([this.player.play(), new Promise((_, reject) => { timer = setTimeout(() => reject(new Error('Playback did not start')), 4000); })]);
    } catch {
      if (token !== this.playbackToken) return;
      this.player?.pause();
      throw new Error('Playback did not start. Check Mac sound output, then choose Play answer again.');
    } finally { clearTimeout(timer); }
  }
  close({ release = false } = {}) {
    if (this.wsAbort) this.cancel();
    if (this.closePromise) {
      if (!release && this.closeRelease) { this.closeRelease = false; this.generation++; this.prepared = null; this.cancelPlayback(); }
      return this.closePromise;
    }
    this.closeRelease = release; this.closing = true;
    this.starting = false; this.startupPhase = 'stopped'; this.sessionAbort?.abort(); this.rejectStarted?.(new Error('Voice start cancelled.'));
    const generation = this.generation, token = this.playbackToken;
    this.closingGeneration = generation;
    if (!release) this.generation++;
    if (!release) { this.prepared = null; this.cancelPlayback(); }
    this.mute(); clearTimeout(this.startupTimer); clearTimeout(this.limitTimer); clearTimeout(this.outputTimer); clearTimeout(this.noInputTimer);
    this.stream?.getTracks().forEach(t => t.stop());
    this.closePromise = (async () => {
      if (!this.closedEvent && this.started && this.channel?.readyState === 'open') {
        const closed = new Promise(resolve => { this.finishClose = resolve; }); this.send({ type: 'session.close' });
        let timer; await Promise.race([closed, new Promise(resolve => { timer = setTimeout(resolve, 10000); })]); clearTimeout(timer);
      }
      // Allow already negotiated RTP frames to drain after the control channel closes.
      if (this.recorder) await new Promise(resolve => setTimeout(resolve, 500));
      if (this.recorder?.state !== 'inactive' && this.recorder) {
        let timer;
        await Promise.race([new Promise(resolve => { this.recorder.onstop = resolve; try { this.recorder.stop(); } catch { this.invalidOutput = true; resolve(); } }), new Promise(resolve => { timer = setTimeout(() => { this.invalidOutput = true; resolve(); }, 1500); })]);
        clearTimeout(timer);
      }
      const contract = this.prepared;
      // Bounded in-memory validation categories; never raw visitor media or provider logs.
      this.lastValidation = { request_id: contract?.request_id ?? null, release_requested: release,
        generation_current: generation === this.generation, playback_current: token === this.playbackToken,
        contract_present: Boolean(contract), display_matches: Boolean(contract && this.validDisplay(contract)),
        final_usage_confirmed: Boolean(this.finalUsageConfirmed), close_reason: this.closedEvent?.reason ?? null,
        commentary_acknowledged: Boolean(this.commentaryAcknowledged), output_invalid: Boolean(this.invalidOutput),
        buffered_chunks: this.chunks.length, buffered_bytes: this.bufferBytes,
        transcript_matches: Boolean(contract && speechWords(this.outputTranscript) === speechWords(contract.text)),
        decode: 'not_attempted' };
      let accepted = release && generation === this.generation && token === this.playbackToken && contract && this.validDisplay(contract) && this.finalUsageConfirmed && this.closedEvent?.reason === 'close_requested' && this.commentaryAcknowledged && !this.invalidOutput && this.chunks.length && speechWords(this.outputTranscript) === speechWords(contract.text);
      let audio;
      if (accepted) {
        try { audio = await this.finalizeAudio(new Blob(this.chunks, { type: this.recorder.mimeType })); this.lastValidation.decode = 'succeeded'; } catch (error) { accepted = false; this.lastValidation.decode = error.message === 'No generated speech in the buffer' ? 'no_generated_speech' : error.message === 'Audio decoding timed out' ? 'timeout' : 'failed'; }
        accepted = accepted && generation === this.generation && token === this.playbackToken && this.validDisplay(contract);
      }
      if (accepted) {
        if (this.timings) this.timings.speech_buffer_ms = Math.round(performance.now() - this.timings.speech_submitted);
        this.ready = { contract, ...audio, transcript: this.outputTranscript, timings: this.timings && { connect_ms: this.timings.connect_ms, speech_buffer_ms: this.timings.speech_buffer_ms } };
        this.notify({ type: 'ready', text: 'Speech matches the displayed answer. Choose Play answer.' });
      } else if (release && contract) this.notify({ type: 'held', text: 'Voice did not match or finish. Read the answer; its sources are available.' });
      this.silence?.stop(); this.silence = null; this.sender = null;
      this.channel?.close(); this.peer?.close();
      this.peer = this.channel = this.stream = this.recorder = null; this.started = false; this.prepared = null;
      this.chunks = []; this.bufferBytes = 0; this.outputTranscript = ''; this.transcript = ''; this.fragments = []; this.delegations.clear();
      this.generation++;
      this.notify({ type: 'stopped', text: this.inputFailure || (accepted ? 'Microphone and connection closed. Speech is ready to play.' : this.finalUsageConfirmed ? 'Voice session closed. Choose Talk for another question.' : 'Microphone stopped. Choose Talk when you are ready.') });
    })().finally(() => { this.closePromise = null; this.finishClose = null; this.resolveStarted = null; this.rejectStarted = null; this.closeRelease = false; this.closing = false; });
    return this.closePromise;
  }
}
if (typeof window !== 'undefined') { window.OpenOracleLive = OpenOracleLive; window.OpenOracleCheckedQuestionFlow = checkedQuestionFlow; window.OpenOracleEraseIntent = eraseIntent; }
if (typeof module !== 'undefined') module.exports = { boundedLiveOperation, checkedQuestionFlow, OpenOracleLive, speechContract, speechWords, trimRemoteAudio, createGeneratedSilence, eraseIntent, closedUsageMetadata };
