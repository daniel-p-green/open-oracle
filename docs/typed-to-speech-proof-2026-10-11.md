# Typed question to validated speech — October 11, 2026

## Actual browser proof

The canonical application completed **typed question → real Strands tool loop → original-source/numeric guards → real OpenAI Decisions acceptance → server-issued receipt → real GPT-Live WebSocket → native browser WAV decode → enabled Play answer**.

Public fixture: “What is the COMBAT tax rate?” The accepted and displayed answer was “The printed tax rate is one-quarter of one cent.” Completed speech transcript matched it. Browser buffer: **218,096 WAV bytes, 4.543 seconds**. Provider closed normally, with final usage **5 seconds**. Native browser decoding succeeded. No microphone calls, playback calls, provider errors or browser script errors occurred. Generation did not enter Speaking. This is a validated playable-buffer proof, **not human audibility**.

Evidence: `evals/ws-app-proof-20261011/actual/result.json`, `actual/validated-buffer-800.png`. The full test exited nonzero **after** speech readiness because its exact erase selector did not match the longer accessible name. The original report retains `phase=failed`; it was not rewritten as a wholly successful run. Accessible and visible names were then aligned, and erase/FAQ were checked without another paid trial.

## Safety and cancellation changes

- Same-origin `/api/live/speech` accepts only `request_id` and a visitor session header. The application retains its own accepted receipt; browser-supplied text, reviews or source assertions cannot authorize a call. Unknown, expired, foreign-session, erased, altered or unaccepted receipts are withheld before paid voice creation. Original file SHA-256, source bindings and numeric validation run again before voice and before response release.
- Speech is bounded, buffered in RAM, closed before release and rechecked against current display/generation/playback identity. Exact transcript, acknowledgement, normal final closure, confirmed final usage and non-silent PCM remain required. No transcript trimming to conceal unapproved words. The whole accepted utterance is displayed; no packet-arrival-based captions or word synchronization claim.
- `/api/erase` invalidates a session, drops its receipt and sets cancellation. The actual installed Strands SDK receives `cancel_signal`; tool/budget/application checkpoints also honor it. Synchronous in-flight provider work cannot be unsent, but remaining local work and release are blocked. Server-side speech subprocesses are terminated on cancellation; final usage may be unknown in that case.
- The accessible Erase this session control stops local capture/playback, revokes audio URLs, clears context/transcripts/source UI, aborts client requests and rejects late callbacks. Spoken exact erase phrases and a small explicit English/Spanish/French/German/Portuguese equivalent set route to reset during active recognition, before ballot retrieval. These phrase fixtures do not prove multilingual recognition accuracy.
- **No ambient listening was added.** When capture is stopped, spoken erase during retrieval/playback cannot be recognized. The accessible control remains available. Provider deletion is never promised. No session-linked feedback collector exists to clear; erased session IDs are tombstones for ten minutes and bounded to 32 records. Receipt availability is three minutes; stale records are pruned on subsequent operations or server restart.
- `/api/data-use` and its text/control entry provide curated facts for the actual configured mode, including payloads, local Strands versus Bedrock mode, disabled cloud hosting/export integrations and OpenAI retention uncertainty. No election model/review is called to answer it. API callers' literal privacy/erase requests bypass the ballot workflow and paid allowance.

## Local checks

96 Python tests passed in an isolated checkout with copied public source fixtures. All existing JavaScript suites passed, including seven new WebSocket client groups. Eight new Python cases cover receipt isolation/forgery/source change/numeric tampering/expiry/erase/concurrent retrieval cancellation. Native headless-browser authored PCM checks passed: real OfflineAudioContext decode, erase after preparation, erase across delayed retrieval, late-answer rejection, FAQ without retrieval, quota remains consumed, zero capture/playback/provider/external requests and zero page errors. These are authored fixtures, distinct from the actual provider result above.

The complete existing main/Copilot exact-source browser regression is recorded separately when it finishes. No formal accessibility, physical Pi sound, multilingual speech or native AG-UI voice acceptance claim.

## Current running app and handoff

The user-rejected visual proposal was reversed in full and remains isolated in task-4. No concept is accepted. Original `web/index.html`, `styles.css` and official orb assets remain intact. App.js changes are functional voice/privacy bindings and the requested erase/data-use labels only.

The old exact-source process PID26672 was verified then refreshed as **PID50392**, still **127.0.0.1:8765**. Current mode is **exact_source**, review and voice off, FAQ and erase APIs active. The existing Pi reverse tunnel was not changed; its device-side reachability must be verified by its owner. No listener, firewall or venue exposure was broadened. No OS update, camera, microphone or desktop UI was touched.

To perform the next supervised audible proof, the core must replace this owned exact-source process with the opt-in `--live --live-voice --live-ws --max-live-requests 1` process on the same port **after coordinating with the foreground UI owner**. Use existing authorized environment credentials internally; do not enter or print them. Reserve one bounded allowance in the existing $50 ledger first. User actions are: type the public question → Show evidence → Prepare spoken answer → inspect readiness → **Play answer**. Confirm what the human actually hears and matches the complete displayed text; stop/erase afterwards. Do not acquire ambient microphone input or auto-play while the user is away.

Node transport dependencies are declared and locked under `scripts/live-ws`: OpenAI7.25.0 and ws8.22.0. The local backend currently resolves the already-installed verified copies through Promptfoo as a fallback. Portable setup can install the lock locally with `npm ci --ignore-scripts`; no such installation or provider secret configuration was performed here. A Pi browser does not need these backend packages.

## Cost and pending integrations

Recorded usage in this browser trial: four Strands calls (2,790 input/82 output tokens), one Decisions call (2,525 input/0 output tokens), and one GPT-Live session (five seconds). No paid session was running at this checkpoint. This does not establish human audibility.

Agent-owned retrieval/receipts review and readability integration remain separately staged. Do not duplicate the research owner's work or represent their synthetic SDK proof as live. Readability needs its pinned CMUdict dependency and explicit typed/tool routing; formula estimates are not comprehension or political-bias scores. Visual experimentation remains held for Daniel's shared exploration.

References: [GPT-Live primary WebSockets](https://developers.openai.com/api/docs/guides/voice-websockets), [OpenAI data controls](https://developers.openai.com/api/docs/guides/your-data). The published GPT-Live data table lists 30-day abuse monitoring; `store=false` and unverified account ZDR do not establish zero retention or cloud erasure.

## Refreshed main/Copilot regression

Existing actual localhost exact-source browser suite passed on both main and Copilot: keyboard questions/disclosure, retained PDF hashes and text, candidate attribution, actual delayed-response rejection after reset,320/800 reflow,48px targets,reduced-motion,secure-context; capture0/live requests0/external requests0/page errors0. Evidence: `evals/ws-app-proof-20261011/exact-source-regression/browser-current.json`. `git diff --check` and current app.js/live.js syntax checks passed. This is not a formal accessibility or physical Pi test.
