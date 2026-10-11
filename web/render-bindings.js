/* Shared trusted catalog binding. Existing owners supply request identities,
 * transport and cancellation. This does not authorize speech or stop a provider. */
(function(root) {
  'use strict';
  function createIngress(isCurrent) {
    let catalog = null;
    const trust = {
      source: id => catalog?.sources[id], contest: id => catalog?.contests[id],
      card: id => catalog?.cards[id], sourceFingerprint: id => catalog?.source_bindings[id],
      get officialLinks() { return catalog?.official_links || []; },
      candidateSource: id => catalog?.candidate_sources[id]
    };
    const store = new root.OpenOracleReleaseStore.AcceptedStore({isCurrent, trust});
    return Object.freeze({
      async prepare(ticket, context, signal) {
        store.invalidate('new_request');
        const query = new URLSearchParams(context.scope);
        const response = await fetch('/api/render-catalog?' + query, {cache:'no-store', signal});
        if (!response.ok) throw Error('Source definitions unavailable. No answer released.');
        const next = await response.json();
        if (!isCurrent(ticket) || signal?.aborted) throw Error('Request stopped. No answer released.');
        // This trusted same-origin endpoint is independently bound to retained
        // sources. It is never constructed from an incoming answer.
        for (const key of ['sources','contests','cards','source_bindings','candidate_sources']) {
          if (!next[key] || typeof next[key] !== 'object' || Array.isArray(next[key])) throw Error('Source definitions unavailable. No answer released.');
        }
        if (!Array.isArray(next.official_links)) throw Error('Source definitions unavailable. No answer released.');
        catalog = next;
        store.begin(ticket, context);
      },
      install: (raw,ticket) => store.install(raw,ticket),
      descriptor: (raw,status,ticket) => store.descriptor(raw,status,ticket),
      invalidate: (reason,options) => store.invalidate(reason,options),
      snapshot: () => store.snapshot()
    });
  }
  root.OpenOracleIngress = Object.freeze({createIngress});
})(window);
