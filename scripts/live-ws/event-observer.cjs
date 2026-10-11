'use strict';
// Opt-in test instrumentation. Not loaded by the visitor application.
(function expose(root) {
  const TEXT_LIMIT = 2048;
  function safeText(value) {
    if (value === null) return null;
    if (typeof value !== 'string') return undefined;
    return value.replace(/Bearer\s+[^\s"'<>]+/gi, 'Bearer [redacted]')
      .replace(/\bsk-[A-Za-z0-9_-]+/g, '[redacted]')
      .replace(/(authorization|password|secret|token)\s*[:=]\s*[^\s"'<>]+/gi, '$1=[redacted]')
      .slice(0, TEXT_LIMIT);
  }
  class LiveEventJournal {
    constructor({ now = () => performance.now(), approvedContent = '', maxEntries = 256 } = {}) {
      if (!Number.isInteger(maxEntries) || maxEntries < 8 || maxEntries > 1024) throw Error('Invalid bounded journal size');
      this.now = now; this.startedAt = now(); this.approvedContent = approvedContent;
      this.maxEntries = maxEntries; this.entries = []; this.sequence = 0; this.dropped = 0;
    }
    add(direction, details) {
      const entry = { sequence: ++this.sequence, monotonic_ms: Math.round(this.now() - this.startedAt), direction, ...details };
      if (this.entries.length >= this.maxEntries) { this.dropped++; return; }
      this.entries.push(entry);
    }
    event(direction, payload) {
      let value;
      try { value = typeof payload === 'string' ? JSON.parse(payload) : payload; } catch { this.add(direction, { type: 'observer_parse_error' }); return; }
      if (!value || typeof value !== 'object' || Array.isArray(value)) { this.add(direction, { type: 'observer_shape_error' }); return; }
      const item = {};
      for (const field of ['type', 'event_id', 'client_event_id', 'reason', 'delegation_id']) {
        const text = safeText(value[field]); if (text !== undefined) item[field] = text;
      }
      for (const field of ['start_ms', 'end_ms']) if (Number.isFinite(value[field])) item[field] = value[field];
      if (Number.isFinite(value.usage?.seconds) && value.usage.seconds >= 0) item.usage_seconds = value.usage.seconds;
      if (Number.isFinite(value.context_window?.usage_ratio)) item.context_usage_ratio = value.context_window.usage_ratio;
      if (value.type === 'error') {
        item.error = {};
        for (const field of ['type', 'code', 'message', 'param', 'client_event_id']) {
          const text = safeText(value.error?.[field]); if (text !== undefined) item.error[field] = text;
        }
        item.error_detail_missing = !value.error || typeof value.error !== 'object';
        item.error_message_clipped = typeof value.error?.message === 'string' && value.error.message.length > TEXT_LIMIT;
        item.error_message_redacted = typeof value.error?.message === 'string' && safeText(value.error.message) !== value.error.message.slice(0, TEXT_LIMIT);
      }
      if (value.type === 'session.output_transcript.delta') item.delta = safeText(value.delta);
      if (direction === 'sent' && typeof value.content === 'string') {
        item.content_length = value.content.length;
        item.content_is_approved_phrase = value.content === this.approvedContent;
        if (item.content_is_approved_phrase) item.content = value.content;
      }
      if (value.type === 'session.started' || value.type === 'session.closed') {
        item.session = {};
        for (const field of ['model', 'status']) {
          const text = safeText(value.session?.[field]); if (text !== undefined) item.session[field] = text;
        }
        if (Number.isFinite(value.session?.expires_at)) item.session.expires_at = value.session.expires_at;
      }
      this.add(direction, item);
    }
    mark(type, fields = {}) {
      const item = { type };
      for (const field of ['method', 'path', 'state', 'kind', 'error_type', 'ice_state', 'signaling_state', 'connection_state', 'transceiver_direction', 'current_direction']) {
        const text = safeText(fields[field]); if (text !== undefined) item[field] = text;
      }
      for (const field of ['status', 'packetsSent', 'packetsReceived', 'bytesSent', 'bytesReceived', 'totalSamplesDuration', 'audioLevel', 'jitter']) {
        if (Number.isFinite(fields[field])) item[field] = fields[field];
      }
      this.add('transport', item);
    }
    snapshot() { return JSON.parse(JSON.stringify({ events: this.entries, dropped: this.dropped, complete: this.dropped === 0 })); }
  }
  function installObserver(window, options = {}) {
    const journal = new LiveEventJournal({ ...options, now: () => window.performance.now() });
    const original = window.RTCPeerConnection.prototype.createDataChannel;
    const peers = new Set();
    window.RTCPeerConnection.prototype.createDataChannel = function observed(...args) {
      const peer = this;
      if (!peers.has(peer)) {
        peers.add(peer);
        for (const name of ['connectionstatechange', 'iceconnectionstatechange', 'signalingstatechange']) {
          peer.addEventListener(name, () => journal.mark(name, { connection_state: peer.connectionState, ice_state: peer.iceConnectionState, signaling_state: peer.signalingState }));
        }
        peer.addEventListener('track', event => journal.mark('remote_track', { kind: event.track.kind, state: event.track.readyState }));
      }
      const channel = original.apply(peer, args);
      journal.mark('data_channel_created', { state: channel.readyState });
      channel.addEventListener('open', () => journal.mark('data_channel_open', { state: channel.readyState }));
      channel.addEventListener('close', () => journal.mark('data_channel_closed', { state: channel.readyState }));
      // This listener precedes application onmessage and survives application cleanup.
      channel.addEventListener('message', event => journal.event('received', event.data));
      const send = channel.send;
      channel.send = function loggedSend(payload) {
        journal.event('sent', payload);
        try { return send.call(this, payload); } catch (error) { journal.mark('data_channel_send_failed', { error_type: error.name }); throw error; }
      };
      return channel;
    };
    return {
      journal,
      async stats() {
        for (const peer of peers) {
          for (const transceiver of peer.getTransceivers()) journal.mark('transceiver', { transceiver_direction: transceiver.direction, current_direction: transceiver.currentDirection });
          try {
            const stats = await peer.getStats();
            for (const item of stats.values()) if (['inbound-rtp', 'outbound-rtp'].includes(item.type) && (item.kind === 'audio' || item.mediaType === 'audio')) journal.mark(item.type, item);
          } catch (error) { journal.mark('stats_unavailable', { error_type: error.name }); }
        }
      },
      detach() { window.RTCPeerConnection.prototype.createDataChannel = original; },
    };
  }
  const api = { LiveEventJournal, installObserver, safeText };
  if (typeof module !== 'undefined') module.exports = api;
  if (root) root.OpenOracleDiagnosticObserver = api;
})(typeof window === 'undefined' ? null : window);
