# Open Oracle lifecycle review: valid bugs and remaining gaps

This is a static review of the supplied source only; nothing was executed, so every reproduction below is traced from the code, not observed. The server-side source, Decisions and speech gates hold in the supplied code. The defects are in the browser lifecycle: reset can lock the kiosk permanently, microphone capture is not bound to the capture token, and the speech states can strand.

## A. Current defects (no sensor producer needed)

Voice items need live voice enabled; they can be reproduced with the existing offline fixtures.

### A1. High: slow close permanently locks the kiosk in `reset`
- **Where:** `interaction.js:4, 63, 69-73`; `live.js:195-204`; `app.js:277-278, 336`.
- **Repro:** Reset (Start again or departure) during an open voice session where `session.closed` takes more than about 4.5 s. `live.close()` may take up to 12 s (10 s ack wait, 0.5 s drain, 1.5 s recorder stop), but `resetTimeoutMs` is 5 s. The race rejects and `resetPending` is never cleared, so every later `reset()` returns the stale promise without re-running cleanup.
- **Effect:** The mic is disabled and `beginThinking()` returns null, so typed questions are dropped silently while the page says "Ready for a new visitor." Only a reload recovers. Even on success, typed submits are silently dropped for the whole reset window.
- **Fix:**
  - Resolve reset on local teardown. Tracks are already stopped synchronously at `live.js:192-193`, and `start()` already refuses while `closePromise` is pending.
  - Let the provider acknowledgement finish in the background.
  - On failure, clear `resetPending` but keep state `reset`, so Start again re-runs cleanup. This keeps "no unverified cleanup, no re-arm".
  - Show "Resetting…" instead of dropping submits.
- **Test:** `onReset` rejects once, then resolves: the first reset stays `reset`, the second re-invokes cleanup and reaches `idle`. Add a live fixture whose `session.closed` arrives at 6 s and assert it ends `idle`.

### A2. High: microphone can go live after the visitor abandoned voice
- **Where:** `live.js:97-99, 55, 162-165`; `app.js:56-58, 277-280, 355-358`.
- **Repro:** Click Speak, and while `getUserMedia` is pending (permission prompt), type a question and submit. `ask()` calls `cancel()`, which finds no stream to stop and does not close the session. When permission resolves, the generation is unchanged, so `session.started` enables the tracks and audio streams to the provider. The interaction state is `thinking` or `answer_ready`, and `capture_ready` is rejected but its return value is ignored.
- **Effect:** If the answer rendered first, `evidenceContext` also finds nothing to stop, and capture runs until the 75 s limit. Transcript deltas then overwrite the question box.
- **Fix:** Track a `starting` flag and have `cancel()` call `close()` when a start is in flight. In the `listening` handler, call `live.close()` if `capture_ready` is rejected.
- **Test:** In `test_live_lifecycle.cjs`, leave `getUserMedia` pending, call `start()` then `cancel()`, grant the stream and deliver `session.started`. Assert the track is stopped, never enabled, and no `listening` event fires.

### A3. Medium: speech states strand, leaving Speak dead and "Speaking" on screen
- **Where:** `app.js:62-78`; `interaction.js:38, 51-53`; `live.js:73, 84, 141, 164, 175, 217`.
- **Repro:**
  - Prepare speech and do not press Play. `ready` sends no signal, the state stays `preparing_speech`, and Speak silently does nothing.
  - During playback, press Next part or type one character. `clearAudio` pauses the audio with no signal: the label still says "Speaking", the button reads "Stop playback" but is disabled, and the state stays `speaking`.
  - A 75 s limit, provider error or overlong output during buffering emits only `stopped`, which maps to `capture_failed` on the capture token. "Preparing speech…" stays forever.
  - `clearAudio` disables the speak button and nothing re-enables it for that answer.
  - Resume after pause is rejected because `playback_started` is not allowed from `conversation`.
- **Fix:**
  - Add `speech_ready` (`preparing_speech` → `answer_ready`) and signal it on `ready`.
  - Route paused and finished back to `answer_ready`, and update the assertion at `test_interaction.cjs:23`.
  - Signal `speech_held` with `answerToken` in `clearAudio` and in the `stopped`/`error` handler.
  - Restore the button and status from `latest?.speech`.
- **Test:** A DOM test of `app.js` asserting, for each trigger, that the state is not `preparing_speech` or `speaking` and that `intent('accessible_control')` succeeds.

### A4. Medium: keyboard focus is destroyed on every part change
- **Where:** `app.js:246, 258-262`; also `236`.
- **Repro:** Tab to "Next part" and press Enter. `controls.replaceChildren()` removes the focused button, so focus falls to `<body>`. The new part is not announced. This happens in exact-source mode today.
- **Fix:** Build the two buttons once and toggle `disabled`, or refocus the region. Give `#adaptive-card` a role and label, mark the content `aria-live="polite"`, and remove `tabIndex` when the card is empty.
- **Test:** After activating Next, `document.activeElement` is inside `#adaptive-card`.

### A5. Medium: budget-exhausted message promises what the server blocks
- **Where:** `server.py:50-59, 237-238`.
- **Repro:** Use up `--max-live-requests`. Every `/api/ask` returns 429 saying "Text and retained sources remain available", but the engine is never called.
- **Fix:** Serve the request from a second `EvidenceLoop(corpus)` with no selector or reviewer. It is labelled `not_run` and has no speech, so the gates are unchanged. Otherwise correct the message.
- **Test:** With a cap of 1, the second request returns either an exact-source answer with `review.status == 'not_run'` and no `speech`, or the corrected text.

### A6. Medium: voice is offered after the single session is spent
- **Where:** `server.py:109, 174-177`; `live.js:97, 134`; `app.js:370-373`.
- **Repro:** After one session per server run, health still reports `gpt_live_buffered`. Each later Speak opens the microphone, gathers ICE, then gets 429.
- **Related:** A close during connect does not abort the session fetch, so the one billable session can be created with no client attached.
- **Fix:** Expose slot availability in health. On 429, call `interaction.configure({voiceReady:false})` and update the note. Abort the fetch from `close()`.
- **Test:** After a 429, `#mic` is disabled and `getUserMedia` is not called again.

### A7. Low to medium: transcript handling
- **Where:** `live.js:58-63`; `app.js:52-54`.
- **Repro:** Deltas that arrive after `delegation.created` overwrite the visitor's review edits and null `selectedId`. Past 2,000 characters the mic mutes silently while the page still says "Listening".
- **Fix:** Ignore deltas once `pendingDelegation` is set or the state is not `listening`. On overflow, stop the tracks and notify `review`.
- **Test:** Edit the box after review, deliver a delta, and assert the edit is preserved.

## B. Seam defects (appear once an adapter is attached)

### B1. High: the typed path and Stop control are hidden repeatedly
- **Where:** `app.js:12`; `interaction.js:30`.
- **Repro:** With a presence adapter and voice ready, every publish in `presence`, `invitation`, `intent` or `listening` sets `input-disclosure.open = false`. A producer that repeats `presence_detected` closes "Type instead" while the visitor is typing, and focus is lost. Pressing Speak collapses the panel that holds "Stop GPT-Live".
- **Fix:** Collapse only on state entry, never when the panel has focus or text. Keep a Stop control outside the disclosure.
- **Test:** In `invitation`, open the disclosure, send another `presence_detected`, and assert it stays open.

### B2. Medium: a wave can predate the invitation, with no capture disclosure shown
- **Where:** `interaction.js:28, 37`; adapter `88-89`; `app.js:12, 15`; `index.html:23`.
- **Repro:** A wave detected at 100 ms and delivered at 600 ms is accepted (the age limit is 2 s), though the invitation appeared at 500 ms. The invitation says only "Wave to begin", and the note that audio goes to OpenAI sits in the collapsed disclosure.
- **Fix:** Record `invitedAt` and reject sensor intents whose producer time precedes it plus a minimum display time. Put the capture disclosure in the invitation text.
- **Test:** A wave with `monotonic_ms` before the invitation returns false and `starts === 0`.

### B3. Medium: the state machine lets a withheld turn reach `speaking`
- **Where:** `interaction.js:51-52`; `test_interaction.cjs:24`.
- **Repro:** `beginThinking()`, then `answer_withheld`, `speech_preparing` (allowed from `conversation`), then `playback_started` ends in `speaking`. Today only `speechContract` in `live.js` stops this; the test checks the direct transition only.
- **Fix:** Add a per-turn `accepted` flag set by `answer_accepted` and required by `speech_preparing` and `playback_started`.
- **Test:** That sequence returns false and the state stays `conversation`.

### B4. Medium: stale presence is treated as present
- **Where:** `interaction.js:22-32`; adapter `82, 88-89`.
- **Repro:** There is no presence timeout, so one `presence_detected` followed by a dead camera gives a permanent invitation. Spoken initiation is then gated on that stale presence. The clock anchor is fixed at registration, so drift past −250 ms or +2 s silently drops every event, including departure.
- **Fix:** Add a heartbeat timeout that sets presence to unknown and the state to idle. Treat out-of-window events as unknown rather than ignoring them.
- **Test:** No camera event for N seconds gives `presence === null` and a later wave is rejected.

### B5. Low
- **`app.js:356`:** `beginVoice` returns silently when `voiceActive` is true. A presenter start during a closing session strands `intent`. Signal `capture_failed` on every non-start exit.
- **`interaction.js:38`:** the accessible control is refused during the 500 ms `presence` dwell while the button looks enabled. Add `presence` to the allowed states.
- **Adapter `90-101`:** a non-string `type` such as `["reset_requested"]` passes the pair check and falls through to `intent(source)`, so a malformed reset starts capture. Require string types and an explicit `start_requested` branch.
- **`app.js:30`:** when an adapter closes itself on error, `sensorAdapter` stays set, and re-attach also requires `idle`, which a mid-conversation camera failure never reaches.

## C. Honest gaps and hypothetical risks
- **Event spoofing:** `synthetic:false`, `sessionId` and capabilities are caller assertions. Any same-origin script can attach and drive start or reset. One huge `sequence` value blocks the adapter. There is no detector-health event for wave or wake.
- **No inactivity reset:** With no producer today, a visitor's question, answer and buffered audio persist until someone presses Start again.
- **Gesture flow:** Review needs a touch or key press, and nothing returns to `invitation` after the first turn.
- **Audio binding:** The recorder runs from track start and only the transcript is compared. Audio the provider does not transcribe would sit in the accepted buffer.
- **Cost:** There is no request cap unless `--max-live-requests` is set (`server.py:53`). Refusals and client-aborted requests still reach the reviewer (`engine.py:67-69`).
- **Wording:** `engine.py:72` says quality checks "did not accept" when live retrieval failed and no check ran.
- **Tests:** `test_interaction.cjs:29` passes on sequence order alone. There are no tests of `app.js`, where most of these defects are.
- **Not supplied, so not vouched for:** `release_block`, the reviewer, `make_fallback`, `view_plan`, `cards`, `agui`, `openai_integrations`, `orb.js`.

## D. Checked and sound in the supplied code
- Presence alone never starts capture.
- Camera error sets presence to unknown, not departure.
- Speech needs a `real_api` accepted review, supported facts and matching evidence bindings, on both server and client.
- Playback starts only on a click and is re-checked against the displayed answer.
- Reset invalidates tokens and stops tracks synchronously.
- Answers are fixed neutral strings, so a missed recommendation pattern cannot produce voting advice.
- Original PDFs are re-hashed on every read.