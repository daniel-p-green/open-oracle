# Single approved public-COMBAT trial — actual result

Daniel directly replied yes approved in task-2; the parent separately confirmed the same $0.35 public-COMBAT-only trial within the existing $5 cap. Automatic approval permitted the exact previously prepared command. It ran once without retries, on an owned ephemeral live server that was stopped afterward. The main 8765 source-only app was not changed. No microphone, ambient capture or audio playback occurred.

## Evidence release passed on this example

The actual gpt-6-luna Strands agent called resolve_contest → search_evidence → read_evidence, selected the retained JCEB COMBAT passage and used four model calls in one question workflow. Aggregate usage was 2790 input/82 output tokens; the same aggregate appears on three trace entries and must not be counted three times. Mechanical source contracts reported supported. The resulting public answer was The printed tax rate is one-quarter of one cent.

Actual Decisions used 2525 input tokens and 0 output tokens. It accepted all seven predicates at the unchanged 0.95 threshold: source support 0.99, no vote recommendation 1.00, viewpoint neutrality 1.00, jurisdiction 0.99, clarity 0.98, abstention 1.00, translation status 1.00. This single pass is not calibration or a guarantee; earlier false accepts/rejects remain relevant.

HTTP 200, current live_strands mode, bound speech contract present. Evidence stages: 5468 ms retrieval/construction, 1 ms application guards, 1271 ms Decisions; total 6741 ms. These are observed timings for one trial, not a latency distribution.

## Voice release failed

Actual GPT-Live session.started and input-audio-muted events arrived. No commentary acknowledgment or output-transcript delta was observed. A provider error event arrived; the original observer retained its type but omitted nested error code/message/client-event fields, so the exact failure cause is not established. session.closed confirmed finalization with reason expired and usage 15 seconds. No accepted audio buffer or transcript was retained; ready=false, playback=false, capture_calls=0, page_errors=[].

The existing proof script merged its UI speech-status text into the report status key. Preserve that raw report; live-voice-result-summary.json explicitly separates answered evidence from failed playback release. The screenshot's Preparing speech label is not evidence of generated or released audio.

## Budget accounting

This fixed trial does not authorize an automatic retest. Recorded usage and accepted/held outcomes are execution evidence; invoice settlement and broad quality claims are separate.

## Concrete diagnostic next step, without another paid call

Compare the receive-only WebRTC setup with the official session-timeline requirements. Current code creates an audio recvonly transceiver with no outbound input track, mutes input and immediately appends commentary. Official guidance permits delegation_id=null for session-wide context, so a null ID is not by itself proof of a protocol violation. It also says context acknowledgment can remain pending when the timeline stops, and instructs callers to keep input audio active, including silence, for speech before a caller speaks. Source: https://developers.openai.com/api/docs/guides/live-conversations.

Missing advancing input audio is a plausible hypothesis for the absent acknowledgment/output, not a confirmed diagnosis of the captured provider error. A follow-up should first prepare an explicitly synthetic silent input track or another documented clock route offline, verify no physical capture/playback, preserve all source/Decisions/buffer-release guards, and retain bounded nested provider error metadata and command correlations. Such a trial changes the receive-only test and needs its own explicit bounded approval; do not rerun the same failing test or silently enable the microphone.

The hardware owner still exclusively owns approved Pi forwarding/device checks. No tunnel was opened by task-2. Real Pi conversation, audible words, hands-free completion, physical wave/departure and boot recovery remain unverified.
