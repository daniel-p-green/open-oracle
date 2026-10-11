# GPT-Live transport diagnosis and repair

Actual provider cause captured: `server_error` / `context_injection_incomplete`, message: “The session closed before the estimated context injection completed.” `param:null`; `client_event_id` exactly matched the outgoing `session.commentary.append`. The error appeared only after our explicit client close, following 20 seconds without context acknowledgement/output. Original trial's expired-session error was not retained; we do not retrospectively identify it.

Controlled sequence (all public fixed sentence, microphone/playback0, same GPT-Live/server instructions/mute):

| Transport | Observation | Final closure |
| --- | --- | --- |
| Existing recvonly | No ack/output; pending-context error after close | close_requested,15 usage seconds |
| AudioContext zero source/sendrecv | Clock reported running but local time0, outbound RTP0; same pending error | close_requested,15 seconds |
| Verified generated PCM-zero/sendrecv | Commentary ack at2768ms; exact transcript “The printed tax rate is one-quarter of one cent.”; no errors;205 inbound packets/29072bytes,265 outbound/9166bytes | close_requested,15 seconds |

Local-only two-peer comparison confirmed AudioContext clock0 failure independent of OpenAI. PCM generator advanced4.24seconds and sent/received211packets; no API/hardware/speaker. This local check prevented another unverified transport claim.

The controlled Live comparison localizes failure to the absent active upstream audio timeline in the receive-only path. A null delegation ID is permitted and was successful with PCM. It is not a proven provider syntax error. [Official session guidance](https://developers.openai.com/api/docs/guides/live-conversations) requires active input, including silence, for proactive speech and explains timeline-dependent append acknowledgements/pending errors at closure.

Canonical `web/live.js` now negotiates a generated PCM-zero upstream track for text-to-speech. When a microphone question reaches review, physical capture ends immediately and its sender is replaced by generated silence. Stop/reset still stop hardware immediately; generated transport cleans up on close. Unsupported generated-track browsers fail closed to text before a text-speech paid session. No Realtime/provider switch. Source/Decisions/display/transcript/acknowledgement/final-closure checks remain unchanged.

New offline checks:5 generator (zeros, timestamps, stop, unsupported support, write failure) +3 transport (physical capture stops at review, text speech device-free, unsupported before paid session). Existing event, stale/reset lifecycle and adversarial buffered-release suites pass against the repair. Observer9groups and browser fixtures pass. These are offline tests, not physical microphone or audible playback evidence. Formal accessibility audit remains deferred; keyboard/text, truthful status, matching readable speech and recovery remain implementation constraints.

Three actual diagnostic sessions each reported15seconds usage (~$0.0125 each). Invoices unconfirmed; reservations held. Full-app proof reserved separately ($0.35) within Daniel's explicit$50 total test cap; result recorded separately when complete. No visitor audio/video/preferences retained; raw diagnostic output covers only a fixed public sentence. Instrumentation is opt-in, not loaded as production visitor telemetry.

## Full-app result and remaining blocker

First full-app attempt: real Strands and Decisions accepted, but copied timer binding root reference failed before any Live request. Fixed globalThis binding; actual-helper browser fixture now passes native generated-frame recording/decoding and fake Play/Stop/reset callbacks. Corrected second full-app attempt: Strands4calls and Decisions accepted again, source facts supported, real GPT-Live commentary acknowledged and exact transcript received, no provider errors, close_requested15seconds. Audio still held (readyfalse; no accepted blob). This is a separate native remote-buffer/decoder release failure; exact condition was not retained by that older observer. Added bounded in-memory lastValidation categories for the next diagnostic; no visitor logs/media. Do not claim audible speech.

Actual playback notifications now carry request_id/validated/playing; app forwards the orb controller required requestId/validated/playing fields. Test integration uses real controller plus authored playback callbacks; physical playback remains unverified.

Next proposed diagnostic: one GPT-Live-only public fixed-sentence session with PCM-zero input; observe remote MediaRecorder data sizes, muted/readyState, actual RTP stats and decode duration/peak in browser memory. No evidence/Decisions rerun, mic, playback or saved media; maximum30seconds plus boundedclose; reserve$0.15 within existing$50 cap before execution. This proposal is not yet executed. Parent should coordinate any actual Mac playback/browser testing with UI owner.
