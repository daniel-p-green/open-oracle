import {answer, immutableCopy} from './core.mjs';

export const RETENTION_NOTICE = Object.freeze({
  version: 'openai-data-controls-2026-10-24',
  text: 'In a future approved cloud session, your microphone audio and transcript would go to OpenAI. OpenOracle will not save recordings or transcripts by default. OpenAI may retain content in abuse-monitoring logs for up to 30 days, with legal or safety exceptions. Live session recording is disabled by default; store:false does not mean zero provider retention. Zero Data Retention requires eligibility and approval. Stop clears local capture and playback but cannot unsend data.',
  url: 'https://developers.openai.com/api/docs/guides/your-data',
});

// The reader alone issues speech eligibility. A caller's status/verified flags
// cannot mint a receipt. This fixture receipt is never live review approval.
export function createEvidenceReader(corpus) {
  const admitted = immutableCopy(corpus);
  const receipts = new WeakSet();
  return Object.freeze({
    async read(question, locale) {
      const result = await answer(question, admitted, locale);
      if (result.status === 'answered') receipts.add(result);
      return result;
    },
    reading(result) {
      if (!receipts.has(result)) throw Error('no_reader_receipt');
      return result.claims.map(claim => claim.text).join(' ') +
        ' This is a retained public sample, not your personal ballot. Current availability and election applicability have not been rechecked.';
    },
  });
}

// Adapter interface (fixture only in this build):
// permission({signal}) -> granted|denied
// capture({signal}) -> {stop()}; no captured bytes enter controller state
// prepare({text,request,signal}) -> {kind,request,transcript,complete,dispose()}
// play(buffer) -> {stop(),finished:Promise}; never autoplay on preparation
// Every adapter operation must cooperate with cancellation; late handles are
// also disposed by this owner. Real media/cloud adapters are deliberately absent.
export function createConversation({session, reader, io, onChange = () => {}, timeoutMs = 5000}) {
  if (io.kind !== 'fixture') throw Error('live_adapters_disabled');
  let state = immutableCopy({stage:'idle', mic:'off', actualCapture:false, consent:false, result:null, reading:'', preview:''});
  let abort, capture, buffer, player, ticket;
  const update = patch => {
    state = immutableCopy({...state, ...patch});
    onChange(state);
  };
  const dispose = resource => { try { resource?.stop?.(); resource?.dispose?.(); } catch { /* Cleanup must not block reset. */ } };
  function cancel(reason = 'stopped') {
    session.reset();
    abort?.abort();
    dispose(capture); dispose(player); dispose(buffer);
    capture = buffer = player = undefined;
    update({stage:reason, mic:'off', actualCapture:false, consent:false, result:null, reading:'', preview:''});
  }
  async function bounded(operation, request) {
    const promise = Promise.resolve(operation);
    promise.then(value => { if (!session.current(request)) dispose(value); }, () => {});
    let timer, onAbort;
    const signal = abort?.signal;
    try {
      const value = await Promise.race([promise, new Promise((_, reject) => {
        timer = setTimeout(() => reject(Error('operation_timeout')), timeoutMs);
      }), new Promise((_, reject) => {
        onAbort = () => reject(Error('operation_cancelled'));
        if (signal?.aborted) onAbort();
        else signal?.addEventListener('abort', onAbort, {once:true});
      })]);
      return session.current(request) ? value : undefined;
    } finally { clearTimeout(timer); signal?.removeEventListener('abort', onAbort); }
  }
  function fail(request) {
    if (!session.current(request)) return;
    cancel('held');
  }
  return Object.freeze({
    snapshot: () => state,
    requestConsent() {
      cancel('consent_required');
    },
    async consent(accepted) {
      if (state.stage !== 'consent_required') return false;
      if (accepted !== true) { cancel('consent_declined'); return false; }
      ticket = session.begin(); const request = ticket;
      abort = new AbortController();
      update({stage:'permission_pending', consent:true});
      try {
        const permission = await bounded(io.permission({signal:abort.signal}), request);
        if (!session.current(request)) return false;
        if (permission !== 'granted') { cancel('permission_denied'); return false; }
        const handle = await bounded(io.capture({signal:abort.signal}), request);
        if (!session.current(request)) return false;
        if (typeof handle?.stop !== 'function') throw Error('capture_contract');
        capture = handle;
        update({stage:'listening', mic:'fixture_active', actualCapture:false});
        return true;
      } catch { fail(request); return false; }
    },
    async completeInput(question, locale = 'en') {
      if (state.stage !== 'listening') return false;
      const request = ticket;
      dispose(capture); capture = undefined;
      update({stage:'checking', mic:'off'});
      try {
        const result = await bounded(reader.read(question, locale), request);
        if (!session.current(request)) return false;
        if (result?.status !== 'answered') {
          update({stage:'held', result:result ?? null, consent:false});
          return false;
        }
        const text = reader.reading(result);
        update({stage:'preparing', result, reading:text});
        const candidate = await bounded(io.prepare({text, request, signal:abort.signal}), request);
        if (!session.current(request)) return false;
        if (candidate?.kind !== 'fixture_audio' || candidate.request !== request || candidate.transcript !== text || candidate.complete !== true || typeof candidate.dispose !== 'function') {
          dispose(candidate); throw Error('audio_binding');
        }
        // Own the admitted metadata; never retain mutable adapter fields as
        // playback authority. This fixture carries no audio bytes.
        buffer = Object.freeze({
          kind:'fixture_audio', request, transcript:text, complete:true,
          dispose:candidate.dispose.bind(candidate),
        });
        update({stage:'ready', consent:false});
        return true;
      } catch { fail(request); return false; }
    },
    play() {
      if (state.stage !== 'ready' || !session.current(ticket) || !buffer || buffer.request !== ticket || buffer.transcript !== state.reading) return false;
      const request = ticket;
      try {
        const handle = io.play(buffer);
        if (!session.current(request)) { dispose(handle); return false; }
        if (typeof handle?.stop !== 'function' || typeof handle?.finished?.then !== 'function') {
          dispose(handle); throw Error('playback_contract');
        }
        player = handle;
        update({stage:'playing', preview:state.reading});
        handle.finished.then(() => {
          if (session.current(request) && state.stage === 'playing') {
            dispose(player); dispose(buffer); player = buffer = undefined;
            update({stage:'complete', preview:''});
          }
        }, () => fail(request));
        return true;
      } catch { fail(request); return false; }
    },
    interrupt: () => cancel('interrupted'),
    reset: () => cancel('idle'),
  });
}

export function createFixtureIO() {
  return Object.freeze({
    kind:'fixture',
    permission: async () => 'granted',
    capture: async () => ({stop() {}}),
    prepare: async ({text, request}) => ({kind:'fixture_audio',request,transcript:text,complete:true,dispose() {}}),
    play() {
      let resolve;
      const finished = new Promise(done => { resolve = done; });
      const timer = setTimeout(resolve, 1500);
      return {finished, stop() { clearTimeout(timer); resolve(); }};
    },
  });
}
