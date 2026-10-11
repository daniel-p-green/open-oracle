// App-owned events only. This adapter neither captures audio nor starts a Live session.
export const AGENT_STATE = Object.freeze({ ready: null, listening: "listening", thinking: "thinking", speaking: "talking", uncertain: null });
const LABEL = { ready: "Ready for a question", listening: "Listening", thinking: "Thinking", speaking: "Speaking", uncertain: "Uncertain — context or evidence needed" };
const gaps = new Set(["clarification", "insufficient_evidence", "conflict", "unavailable", "neutrality_boundary"]);
const level = value => Number.isFinite(value) ? Math.max(0, Math.min(1, value)) : 0;
export function createOrbController() {
  let value = Object.freeze({ sessionId: "visitor-0", requestId: null, releasedRequestId: null, state: "ready", label: LABEL.ready, inputLevel: 0, outputLevel: 0 });
  const listeners = new Set();
  const commit = change => {
    value = Object.freeze({ ...value, ...change });
    listeners.forEach(fn => fn());
    return true;
  };
  return {
    getSnapshot: () => value,
    subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); },
    dispatch(event) {
      if (!event || typeof event !== "object") return false;
      if (event.type === "visitor-reset") {
        if (typeof event.sessionId !== "string" || !event.sessionId) return false;
        return commit({ sessionId: event.sessionId, requestId: null, releasedRequestId: null, state: "ready", label: LABEL.ready, inputLevel: 0, outputLevel: 0 });
      }
      if (event.sessionId !== value.sessionId) return false;
      const set = state => commit({ state, label: LABEL[state], inputLevel: 0, outputLevel: 0 });
      switch (event.type) {
        case "connection-started":
          return commit({ state: "thinking", label: "Connecting — microphone not active", inputLevel: 0, outputLevel: 0 });
        case "capture-started":
          // The caller must verify a live, enabled audio track after session.started.
          return event.captureActive === true ? set("listening") : false;
        case "capture-stopped": return set("ready");
        case "request-started":
          if (typeof event.requestId !== "string" || !event.requestId) return false;
          return commit({ requestId: event.requestId, releasedRequestId: null, state: "thinking", label: LABEL.thinking, inputLevel: 0, outputLevel: 0 });
        case "answer-released":
          if (event.requestId !== value.requestId) return false;
          if (event.status === "answered") return commit({ releasedRequestId: event.requestId, state: "ready", label: LABEL.ready, inputLevel: 0, outputLevel: 0 });
          return gaps.has(event.status) ? commit({ releasedRequestId: null, state: "uncertain", label: LABEL.uncertain, inputLevel: 0, outputLevel: 0 }) : false;
        case "playback-started":
          // Output deltas, held audio and a successful model response never imply playback.
          if (event.requestId !== value.requestId || event.requestId !== value.releasedRequestId || event.validated !== true || event.playing !== true) return false;
          return set("speaking");
        case "playback-stopped":
          return event.requestId === value.requestId ? set("ready") : false;
        case "evidence-gap":
          if (event.requestId != null && event.requestId !== value.requestId) return false;
          return commit({ releasedRequestId: null, state: "uncertain", label: LABEL.uncertain, inputLevel: 0, outputLevel: 0 });
        case "input-review":
          return commit({ releasedRequestId: null, state: "uncertain", label: "Review the transcript — audio held", inputLevel: 0, outputLevel: 0 });
        case "output-held":
          return commit({ releasedRequestId: null, state: "uncertain", label: "Generated audio held — no playback", inputLevel: 0, outputLevel: 0 });
        case "connection-error":
          return commit({ releasedRequestId: null, state: "uncertain", label: "Connection unavailable — use text input", inputLevel: 0, outputLevel: 0 });
        case "input-level":
          return value.state === "listening" ? commit({ inputLevel: level(event.level) }) : false;
        case "output-level":
          return value.state === "speaking" && event.requestId === value.requestId ? commit({ outputLevel: level(event.level) }) : false;
        default: return false;
      }
    }
  };
}

