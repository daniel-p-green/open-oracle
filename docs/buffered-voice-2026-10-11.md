# Buffered voice implementation — 2026-10-11

Historical checkpoint: the main browser had a complete buffered spoken-answer path. Real provider speech and human audibility had not been verified in this pass; no new provider request or microphone capture ran. See the later public evidence summary for the separately retained No buffer result.

## Release path

1. `Speak` requests microphone permission only on the visitor's click. GPT-Live input is disabled until session startup. A client delegation stops the microphone tracks and presents the transcript for review/correction. Partial transcription never runs evidence tools.
2. `Show evidence` runs the existing substantive Strands resolve/search/read workflow, immutable source/finite-fact checks and **the real OpenAI Decisions API**. Decisions retains the frozen seven predicates, .95 threshold and `not_validated` calibration label. No ordinary LLM judge replaces it.
3. Only a supported English answer accepted by real Decisions receives a speech contract with request identity, exact visible text and retained evidence bindings. There is no extra rewrite model or softened threshold.
4. GPT-Live receives that exact sentence as client commentary. Incoming **remote generated output only** is recorded in memory; it is never directly attached to a player. Microphone audio is not recorded by MediaRecorder or saved by this app; microphone input is sent to OpenAI only after explicit capture consent. Sessions use `store:false`.
5. GPT-Live has no transcript-done event. A quiet interval schedules closure; it does not authorize release. Confirmed `session.closed` with `close_requested`, commentary acknowledgment, bounded buffer, complete transcript word match and current visible text/source-bound contract are required. Unexpected earlier output, mismatch, provider error, missing final event and stale identity withhold playback. The provider transcript is fallible and is not an independent acoustic verification.
6. A bounded OfflineAudioContext decodes the buffer without opening the Mac audio device. Leading/trailing silence is trimmed conservatively and encoded as local WAV. `Play answer` is a separate user action. Speaking follows actual local playback callbacks, not generation events. Playback startup has a four-second bound and offers a free local retry after checking Mac output.
7. Question editing, answer-step navigation, reset, page exit and Escape stop/discard queued audio. Reset disables Speak until the old connection closes. The current source view and entire accepted English utterance remain readable. No timed word highlighting is claimed.

Server constraints: loopback-only live voice, one billable Live session per server run, 75-second client session limit, 8 MiB output bound, four-second decode bound, bounded recorder/connection shutdown. `--max-live-requests 1` caps paid evidence requests across both `/api/ask` and `/api/ag-ui`; no automatic model retries. Existing per-request Strands attempt/token/message limits remain. Local CSP permits only same-origin or in-memory blob media; no external script/network allowance was added.

## Experience and timing

The full accepted sentence is visibly readable before playback. The rate card no longer repeats the lead sentence, and candidate comparisons no longer repeat a roster. Existing approved cards, original wording and actual controlled CopilotKit tool rendering remain. No design concept was selected, and freeform generated executable UI remains disabled. Short accepted-stage opacity changes honor reduced motion.

The response now records `stage_ms` for resolve/retrieve/construct, source guards and Decisions. Voice retains connection and buffered-speech timings. The refreshed exact-source COMBAT request measured 1 ms construction, 1 ms guards, 0 ms Decisions (off); these are **local measurements, not live latency measurements**. No real provider latency was measured in this pass.

## Verification completed

- 76/76 Python tests, including speech release conditions and shared paid-request cap.
- 51/51 offline Promptfoo application cases; zero model calls.
- JavaScript syntax, three offline Live event/lifecycle/buffer adversarial suites and whitespace checks.
- Actual browser MediaRecorder on a synthetic WebCodecs audio track, actual offline decoding/WAV generation, visible-text binding, reset and denied microphone path. Provider events and UI playback callbacks are explicitly offline fixtures.
- Native headless playback clock intermittently stalled at currentTime 0 despite a valid 2.1-second WAV and no media error. Other attempts reached playback/stop, but this is **not reliable native or human audible proof**. The app now times out cleanly instead of hanging.
- Main and actual CopilotKit browser rate/duration/step views and poisoned-card source fallback pass with no external calls, capture, iframe or page errors.
- Canonical CopilotKit TypeScript and bundle build pass after installing the lockfile from local cache with `npm ci --offline --ignore-scripts --no-audit --no-fund`.

Proof files are in `evals/buffered-voice-20261011/` and task-2 `voice-integration/`. These are application/offline tests, not evaluator calibration. Previously measured Decisions false accepts and false rejects remain documented; no further calibration calls or changed thresholds were used.

## Exact next interaction

Currently running: **http://127.0.0.1:8765/**, text/exact-source mode; `/copilot` remains the controlled text renderer. Frontend/API share port8765, listener127.0.0.1, task-owned server session36673. No Pi-reachable LAN/HTTPS URL exists. No network/security settings or Pi OS/hardware work changed.

A future live proof requires explicit capped authorization: one fixed public COMBAT Strands evidence request and independent Decisions check, followed by one receive-only GPT-Live session. No new credentials, microphone, automatic playback or retry. The prepared harness had not run at this checkpoint.

Run commands from `/Users/danielgreen/Documents/Codex/open-oracle`. The current text-only server uses `.venv/bin/python -m open_oracle.server --host 127.0.0.1 --port 8765`; do not start a second process on that port.

After that proof and a separately reserved human test are approved, stop the task-owned text server and launch with the existing permitted credential in the process environment:

```sh
OPEN_ORACLE_ALLOW_LIVE=1 OPEN_ORACLE_MODEL=gpt-6-luna .venv/bin/python -m open_oracle.server --host 127.0.0.1 --port 8765 --live --live-voice --max-live-requests 1
```

Do not start this enabled mode to work around the approval rejection. It creates no provider request at startup, but clicking the controls can spend money and send data.

Daniel's short microphone test: open `/`, click **Speak**, grant microphone access, say **“What is the COMBAT tax rate?”**, inspect/correct the transcript, choose **Show evidence**, then **Play answer** only when ready. Confirm that the audible words match the visible sentence **“The printed tax rate is one-quarter of one cent.”** and its original source, then use **Stop playback** or **Start again** during sound. If checks reject or speech differs, the text/source fallback is the honest result; do not lower the threshold or claim success. Typed-question + Prepare spoken answer is the receive-only fallback and needs no microphone.

## Remaining blockers and limits

Actual Strands/Decisions/GPT-Live answer release and human microphone/audibility alignment remained unrun in this pass. No provider request ran.

English only; changed/transformed speech is withheld. Voice jurisdiction/source-gap replies currently use text and originals. Pi has no verified capture source or approved reachable secure URL. Real Lumina capture/wave trigger, physical Pi legibility, translated speech and full duplex are unverified. Camera remains optional staging. Research, source originals, memories, AWS resources, credentials, desktop browser, Pi OS and network configuration were not changed.


## 2026-10-11 00:19 UTC — authorized single retry rejected before execution

The proposed repeated trial did not execute. No alternate provider or indirect execution followed; actual human microphone and audible output remained unverified.

When recognized direct approval permits the live mode, Daniel’s Mac microphone check is: open http://127.0.0.1:8765/; click Speak and grant microphone permission; say “What is the COMBAT tax rate?”; review/correct the transcript and click Show evidence; when validated, click Play answer and compare the audible words to “The printed tax rate is one-quarter of one cent.”; use Stop playback or Start again. Do not enable/capture remotely before consent. Current server remains text-only with Speak disabled.


Offline readiness rechecked at 2026-10-11 00:23 UTC: both actual localhost routes preserve sources, keyboard disclosure and Reset/stale-response guards. Both original PDF hashes match. See `evals/offline-readiness-20261011` and the precise test gaps in log.md. The live command remains documentation only; no denied call was retried in this pass.
