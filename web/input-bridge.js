'use strict';
// Same-origin metadata polling only. No camera, microphone, detector or event injection endpoint.
class OracleInputBridge {
  constructor(inputs, { fetcher = (...args) => fetch(...args), delay = 250 } = {}) {
    this.inputs = inputs; this.fetcher = fetcher; this.delay = delay; this.generation = 0; this.cursor = 0; this.adapter = null; this.session = null;
  }
  detach() { this.adapter?.close(); this.adapter = null; this.session = null; }
  async poll(generation) {
    try {
      const response = await this.fetcher('/api/input-events?after=' + this.cursor, { signal: this.abort.signal, cache: 'no-store' });
      if (generation !== this.generation) return;
      if (!response.ok) throw Error('Input transport unavailable');
      const body = await response.json();
      if (generation !== this.generation) return;
      if (body.schema !== 'open-oracle-input/v1' || !Number.isSafeInteger(body.cursor) || body.cursor < this.cursor || !Array.isArray(body.events) || body.events.length > 64) throw Error('Invalid input metadata');
      this.cursor = body.cursor;
      if (body.available !== true || body.discontinuity === true) { this.detach(); return; }
      if (body.session_id !== this.session) {
        this.detach();
        if (this.inputs.snapshot().state !== 'idle') return;
        this.adapter = this.inputs.attachSensorAdapter({ sessionId: body.session_id, producerMonotonicMs: body.producer_monotonic_ms,
          sources: ['camera','camera_wave','spoken_initiation','presenter_key','presenter_click'], capabilities: body.capabilities });
        this.session = body.session_id;
        return; // Never replay retained start/reset signals to a newly attached visitor/tab.
      }
      for (const event of body.events) this.adapter?.accept(event);
    } catch { if (generation === this.generation) this.detach(); }
    finally { if (generation === this.generation) this.timer = setTimeout(() => this.poll(generation), this.delay); }
  }
  start() { this.stop(); this.abort = new AbortController(); const generation = this.generation; this.poll(generation); }
  stop() { this.generation++; clearTimeout(this.timer); this.abort?.abort(); this.detach(); }
}
if (typeof module !== 'undefined') module.exports = { OracleInputBridge };
if (typeof window !== 'undefined') window.OracleInputBridge = OracleInputBridge;
