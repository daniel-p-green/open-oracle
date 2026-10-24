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

// Completed jobs still own server-held results until explicitly revoked.
// Reuse this for Erase after polling/transport has already finished.
export async function cancelProviderJob({ requestId, token, fetcher = fetch }) {
  if (!requestId || !token) return false;
  try {
    const response = await fetcher("/api/provider/cancel", {
      method: "POST", cache: "no-store", keepalive: true,
      headers: { "Content-Type": "application/json", "X-Session-Token": token },
      signal: AbortSignal.timeout(3000),
      body: JSON.stringify({ request_id: requestId }),
    });
    if (response.ok) return true;
    // The authenticated local server expires/clears owner-held rows before
    // returning this exact error. Other conflicts/failures stay unconfirmed.
    if (response.status === 409) {
      const failure = await response.json();
      return failure?.error === "owner_unavailable";
    }
    return false;
  } catch { return false; }
}

// Opaque request ownership only: no visitor content, no automatic retry.
// A failed explicit revoke remains available for the next deliberate Erase.
export function createProviderRevocation({ token, isCurrent, fetcher = fetch }) {
  let id = null, pending = false, revoking = null;
  return {
    get retained() { return id !== null; },
    get pending() { return pending; },
    onRequest(value) {
      if (!isCurrent()) return;
      pending = value !== null;
      if (value) id = value;
    },
    revoke() {
      pending = false;
      if (!id) return Promise.resolve(true);
      if (revoking) return revoking;
      const owned = id;
      revoking = cancelProviderJob({requestId: owned, token, fetcher}).then(ok => {
        if (ok && id === owned) id = null;
        return ok;
      }).finally(() => { revoking = null; });
      return revoking;
    },
  };
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
  onTiming = () => {},
  onProgress = () => {},
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
  const cancel = () => cancelProviderJob({ requestId: id, token, fetcher });
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
            "speech_too_long",
          ].includes(denial.error)
        )
          onNotStarted(denial.error);
      } else if ([400, 403, 405].includes(response.status)) {
        // These exact local-server errors precede Jobs.start. A 5xx/transport
        // failure may have occurred after dispatch; never call that no-start.
        const denial = await response.json();
        const preDispatch = {
          400: "request_invalid",
          403: "unexpected_origin",
          405: "provider_and_intake_routes_disabled",
        };
        if (denial.error === preDispatch[response.status])
          onNotStarted(denial.error);
      }
      throw Error("provider_held");
    }
    let job = await response.json();
    while (session.current(ticket) && !operationSignal.aborted) {
      if (job.request_id !== id) throw Error("request_mismatch");
      if (
        Array.isArray(job.updates) &&
        !["held", "cancelled", "expired", "cancel_requested"].includes(
          job.state,
        )
      )
        onProgress(job.updates);
      if (job.state === "ready") {
        onTiming(job.timing);
        return decode(job.result, {
          requestId: id,
          expiresInSeconds: job.expires_in_seconds,
        });
      }
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
