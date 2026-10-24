import { baselineLayout, validateLayout } from "./experience-core.mjs";
// The operation timeout owns fetch, body consumption and polling. No visitor
// string enters this client: the only provider input is an admitted intent ID.
export async function requestLayout(options) {
  const { intent } = options;
  const fallback = () => ({
    layout: validateLayout(baselineLayout(intent), intent),
    mode: "fallback",
  });
  if (
    !options.token ||
    ![
      "effects",
      "rate",
      "duration",
      "purpose",
      "maps",
      "candidates",
      "unknown",
    ].includes(intent)
  )
    return { ...fallback(), mode: "local" };
  return requestProviderJob({
    ...options,
    task: "layout:" + intent,
    fallback,
    decode: (result) => ({
      layout: validateLayout(result.layout, intent),
      mode: "live",
    }),
  });
}

// Shared transport/ownership path for layout and fresh evidence answers.
export async function requestProviderJob({
  task,
  parentRequest = null,
  fallback,
  decode,
  ticket,
  session,
  token,
  signal,
  onRequest = () => {},
  onNotStarted = () => {},
  fetcher = fetch,
  timeoutMs = 25000,
}) {
  if (signal.aborted || !session.current(ticket)) return null;
  const id = crypto.randomUUID().replaceAll("-", ""),
    controller = new AbortController();
  onRequest(id);
  let timer;
  const deadline = new Promise((_, reject) => {
    timer = setTimeout(() => {
      controller.abort();
      reject(Error("layout_timeout"));
    }, timeoutMs);
  });
  const operationSignal = AbortSignal.any([controller.signal, signal]);
  const opts = {
    headers: { "Content-Type": "application/json", "X-Session-Token": token },
    signal: operationSignal,
    cache: "no-store",
  };
  const cancel = () =>
    fetcher("/api/provider/cancel", {
      ...opts,
      method: "POST",
      signal: AbortSignal.timeout(3000),
      body: JSON.stringify({ request_id: id }),
      keepalive: true,
    }).catch(() => {});
  const work = async () => {
    const response = await fetcher("/api/provider/start", {
      ...opts,
      method: "POST",
      body: JSON.stringify({
        request_id: id,
        question_id: task,
        ...(parentRequest ? { parent_request_id: parentRequest } : {}),
      }),
    });
    if (!response.ok) {
      if (response.status === 409) {
        const denial = await response.json();
        if (
          [
            "parent_unavailable",
            "run_limit",
            "busy",
            "owner_unavailable",
            "budget_exhausted",
            "request_conflict",
            "cancelled",
          ].includes(denial.error)
        )
          onNotStarted(denial.error);
      }
      throw Error("provider_held");
    }
    let job = await response.json();
    while (session.current(ticket) && !operationSignal.aborted) {
      if (job.request_id !== id) throw Error("request_mismatch");
      if (job.state === "ready") return decode(job.result);
      if (
        ["held", "cancelled", "expired", "cancel_requested"].includes(job.state)
      )
        throw Error("layout_held");
      await new Promise((resolve) => setTimeout(resolve, 200));
      if (!session.current(ticket) || operationSignal.aborted)
        throw Error("cancelled");
      const poll = await fetcher("/api/provider/job/" + id, opts);
      if (!poll.ok) throw Error("layout_unavailable");
      job = await poll.json();
    }
    throw Error("cancelled");
  };
  try {
    const result = await Promise.race([work(), deadline]);
    if (!session.current(ticket) || signal.aborted) {
      cancel();
      return null;
    }
    return result;
  } catch {
    cancel();
    return session.current(ticket) && !signal.aborted ? fallback() : null;
  } finally {
    clearTimeout(timer);
    controller.abort();
    onRequest(null);
  }
}
