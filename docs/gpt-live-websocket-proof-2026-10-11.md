# GPT-Live voice checkpoint — October 11, 2026

## Verified result

The actual `gpt-live-1` primary WebSocket produced a validated **3.765-second WAV buffer** in memory for:

> The printed tax rate is one-quarter of one cent.

`evals/live-diagnosis-20261011/real-ws-03/result.json` retains the bounded event journal and validation. Exact normalized transcript, application commentary acknowledgement, final `session.closed` with `reason=close_requested`, final usage of **4 seconds**, valid bounded PCM and non-silent signal all passed. Raw output: 210,240 PCM bytes; peak 0.3164; RMS 0.0380. Trimming removed 615 milliseconds of leading/trailing silence, preserving 150-millisecond padding. No provider errors. The generated WAV remained in RAM and was discarded; no audio file was saved, microphone acquired or playback attempted. **Human audibility is unverified.**

The evidence text came from the same public sentence already accepted by the actual Strands retrieval/source-binding/Decisions full-app workflow. This standalone transport trial did not itself invoke retrieval or Decisions, and is **not yet an end-to-end app voice release**.

## Exact diagnosis and controlled comparisons

- Full-app-03: actual Strands and Decisions accepted; display/request/source contract, commentary acknowledgement, final closure and exact voice transcript passed. Browser `MediaRecorder` yielded zero chunks/bytes, so decoding was never attempted. This was an audio acquisition failure, not a policy gate or source failure.
- Offline two-peer WebRTC tests reproduced 210+ received RTP packets with zero decoded samples/recorded bytes, both with and without headless Chrome's global mute. This supports an execution-environment WebRTC receive limitation; it does not establish foreground-browser behavior.
- WebSocket01: the parser wrongly required an audio event ID. Primary WebSocket audio chunks omit it. Local rejection closed early and the provider reported incomplete context injection; final usage zero seconds. Parser corrected and regression added.
- WebSocket02: acknowledgement and PCM arrived, but the model added unapproved words. The full transcript was correctly held. Final usage 44 seconds. Audio includes continuous silence, so resetting the closure timer on every audio chunk was also incorrect.
- WebSocket03: restored the exact global instructions previously successful over WebRTC; only transcript progression schedules closure, and divergent text causes immediate withholding/closure. All validation passed. No transcript chopping or policy relaxation.

## Local validation

29 local groups passed: observer 9; generated silent transport 5; physical-capture shutdown/sender replacement 3; voice release categories 5; WebSocket PCM/transcript/closure/reset buffer 7. These use authored fixtures, with zero provider calls, microphone calls or physical audibility claims. Tests reject missing acknowledgement, changed transcript, incomplete closure, silent audio, malformed/odd/oversized PCM, duplicate identified events, delegation/error events and erased buffers. Transport ordering permits audio chunks without optional IDs.

## Budget

Daniel explicitly authorized $50 total API testing. Retained reservations: **$6.25**; unallocated: **$43.75**. Cumulative recorded OpenAI usage estimate after this result: **$0.1434314**. Reservations remain held. These are usage-based estimates at referenced prices, **not invoices**, and do not settle any AWS or separate subscription billing. No further paid trial is currently reserved or running.

## Integration handoff and remaining work

Canonical visual files were left unchanged for the isolated task-4 design preview. Existing main server remains loopback-only at `http://127.0.0.1:8765`, exact-source mode; this URL does **not** yet expose the WebSocket proof to visitors. No listener, firewall, tunnel or venue exposure change was made.

Reusable transport staging is in `diagnostics/live/ws-speech.cjs` and pure buffer gate in `ws-buffer.cjs`. The local backend already has the required OpenAI SDK and `ws` through the installed Promptfoo dependencies. This path needs a deliberate dependency/runtime declaration before it becomes portable. `--trusted-stdin` is a prepared server-side transport seam, not a safe public endpoint by itself.

Next integrate a bounded in-memory **server-issued accepted-answer receipt**. `/api/ask` must retain only a current accepted speech contract; a speech request supplies its identity, never browser-asserted review/source/text. Recheck retained source binding before render. Keep the existing frontend request/generation/current-display/playback-token guards and explicit user Play action. Do not let a forged client `review=accepted` authorize a paid speech call. Cancellation must discard output and prevent late release.

Then reserve one bounded full-app trial and coordinate a foreground, user-clicked Mac Play test with the parent/hardware UI owner. No headless test can establish that Daniel heard the answer. Do not replace GPT-Live with Realtime or weaken source/Decisions checks.

New priority requirements are **acknowledged, not implemented in this checkpoint**: spoken “erase this session” and language equivalents must bypass election retrieval during active capture; accessible erase must stop local capture/playback, clear ephemeral context/transcripts/UI and unsent session-linked feedback, invalidate late events and return idle. When capture is stopped, always-available spoken recognition needs a separately supported, authorized capture route; do not imply an always-listening listener exists. Already-sent provider requests cannot be retroactively unsent. The curated data-use FAQ must describe actual configured providers/services, payloads and retention without promising provider erasure.

Current code inspection: Strands runs locally; OpenAI model/Decisions/voice calls are explicit opt-in. Bedrock is an alternate explicitly selected mode, not used in the trials above. No KB, AgentCore hosting, CloudWatch export or CloudTrail data-retention policy was verified from the local app code. Do not equate installing Strands/OpenTelemetry or prior workshop STS/catalog checks with production AWS processing. Raw visitor questions/IPs are not emitted by the HTTP handler; diagnostics here use only the preapproved public fixture, and no visitor audio/video files were collected.

OpenAI's current official data-control table lists `/v1/live/sessions` abuse-monitoring retention of 30 days and application state of none, or 30 days if stored. App sessions set `store=false`; the account's ZDR eligibility/settings were not inspected. Do not claim local reset erases provider-held data.

Official references: [GPT-Live primary WebSockets](https://developers.openai.com/api/docs/guides/voice-websockets), [OpenAI data controls](https://developers.openai.com/api/docs/guides/your-data).

## Typed demo preservation

Fresh offline invocation of the same real EvidenceLoop/Corpus answered the COMBAT rate with source-supported `one-quarter of one cent`; the request to recommend YES returned `neutrality_boundary` and no evidence or voting advice. Zero API calls; independent review `not_run`, not a new Decisions proof. Result: `evals/live-diagnosis-20261011/typed-demo-checkpoint.json`. `git diff --check`, app.js/live.js syntax checks passed.
