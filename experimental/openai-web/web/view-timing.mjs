// One action's numeric timings in the current DOM only. No text, source history,
// storage, analytics or provider transmission. A stale turn cannot write marks.
const MARKS = new Set([
  "intent_routed",
  "evidence_checked",
  "first_source",
  "maps_validated",
  "first_useful_visual",
  "stable_view",
  "checked_text",
  "audio_ready",
]);
export function createViewTiming(
  host,
  scope,
  current,
  now = () => performance.now(),
) {
  if (!["view", "answer", "audio"].includes(scope)) throw Error("timing_scope");
  const started = now(),
    marks = {};
  let backend = null;
  const publish = () => {
    if (current())
      host.dataset[scope + "Timing"] = JSON.stringify({
        basis: "client_action_monotonic_not_human_playback",
        marks_ms: marks,
        ...(backend ? { server: backend } : {}),
      });
  };
  const mark = (name) => {
    if (!MARKS.has(name)) throw Error("timing_mark");
    if (!current() || name in marks) return;
    marks[name] = Math.round(Math.max(0, now() - started) * 1000) / 1000;
    publish();
  };
  publish();
  return Object.freeze({
    mark,
    backend: (value) => {
      if (!value || value.basis !== "server_monotonic_job_not_user_playback")
        return;
      const allowed = new Set([
        "queued",
        "routing",
        "retrieval",
        "text",
        "validation",
        "review",
        "audio",
        "transcription",
      ]);
      const finite = (n) =>
        typeof n === "number" && Number.isFinite(n) && n >= 0 && n <= 240000;
      if (
        !finite(value.elapsed_ms) ||
        !value.stages_ms ||
        Object.entries(value.stages_ms).some(
          ([name, duration]) => !allowed.has(name) || !finite(duration),
        )
      )
        return;
      backend = {
        elapsed_ms: value.elapsed_ms,
        stages_ms: { ...value.stages_ms },
      };
      publish();
    },
    paint: (name) =>
      requestAnimationFrame(() => requestAnimationFrame(() => mark(name))),
  });
}
