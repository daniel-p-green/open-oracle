# Checked-speech delivery correction — technical review draft

October25,2026. Unpaid investigation only. No renderer implemented/enabled, model
eligibility checked, new API run, credential/access change, merge or deployment.
This document proposes a technical correction; it is not a paid job or a new
approval record. The previous bilingual package remains paused with its immutable
English hold and usage evidence.

## Finding and smallest viable change

Actual `native_bilingual_3541a97aff140392` on `dec4164` received a paraphrase of a
checked120-character public answer and correctly held `voice_output_diverged`.
No output-ASR/audio approval or map follow-up occurred. This is a demonstrated
mismatch between the selected output channel and our exact-reading contract,
not evidence of a broken word checker or a language-choice failure.

Official Live delegation docs describe `session.commentary.append` as information
to speak while paraphrasing. `session.instructions.append` guides behavior; its
acknowledgment does not guarantee delivery or exact words. Keeping a backend
result pending does not mute all Live speech. App-controlled playback and its
strict gate remain necessary. Do not spend the conditional repair on another
unchanged exact-reading prompt.

Recommendation: preserve GPT-Live input/caption/native Decisions interaction,
grounded Responses and typed evidence UI, but render each **fresh checked text**
through one isolated OpenAI Realtime response. Buffer and independently verify
that complete waveform before any playback. Drop all native Live output at the
player/relay while this mode is selected; a mute instruction is insufficient.
This is dynamic narration of the actual current answer, not a prerecorded answer
catalog or replacement of adaptive conversation with fixed clips.

This is a **material internal audio-boundary change**, not a one-line prompt fix.
It adds `gpt-realtime-2.1-mini` and Realtime lifecycle/token accounting to the
requested Live+Decisions+Responses design. It preserves product scope, source
policy, OpenAI provider/account and exact-word safety contract, but must be
explained and technically reviewed before wiring or paying for it. Account
availability and improved exactness/latency are not established by documentation.

## Options considered

| Option | Assessment |
| --- | --- |
| More Live commentary/instruction exact-read prompts | No supported verbatim guarantee; real trial demonstrates failure. Not a justified unchanged paid retry. |
| Existing `OpenAIProvider.speak()` / FreshSpeech path | `_speak()` is also GPT-Live, using commentary or exact-reading instructions and quiet-to-close. It is not an independent renderer and cannot be relabeled as TTS. Reuse its checked-parent/whole-WAV-ASR contract, not its transport. |
| Permit source-faithful native paraphrase | Could preserve native voice, but changes the exact transcript/UI delivery contract and adds approval of actual spoken prose. Requires completion/segmentation and factual/number/polarity/citation validation before playback; relaxing equality alone is unsafe. Not selected for the minimal correction. |
| Legacy `/v1/audio/speech` with `tts-1`/`tts-1-hd`/`gpt-4o-mini-tts` | True text-input speech API and potentially smaller adapter, but all three are deprecated for Jan6,2027 shutdown. Do not build the long-term showcase around it or pass Realtime Mini to that endpoint. At most a separately justified temporary comparator. No call proposed here. |
| Isolated Realtime Mini narration | Preferred correction to evaluate. Official TTS migration target; explicit response/item IDs and terminal response status. Still generative, so exactness must be measured and independently checked, not promised. |
| Local macOS speech/Whisper or prerecorded public clips | Useful fixture tools, not the requested OpenAI production speech experience. No new local installation or Pi change. |

## Reuse existing work

- `journey.py`: admitted source packet, exact source/version checks, fresh EN/ES
  generation, independent review and checked parent. Do not replace with model
  memory or broaden candidate/ballot coverage.
- `fresh_speech.py`: whole final PCM→WAV, independent Transcribe without expected-
  text/language hints, exact closed normalization, language and source recheck.
- `voice_agent.py`: one conversation owner, native view/delivery/language choices,
  exact input-caption ownership, per-turn diagnostics, cancellation-owned ASR
  metering and native financial settlement. Do not add another voice controller.
- `voice-core.mjs`/`voice.mjs`: turn/revision/source/language validation, final versus
  provisional captions, source-backed canvas and private reset. Shared checked
  utterance supplies speech and UI; the renderer cannot select arbitrary facts.
- Later Pi project inspected read-only: `server/voice.ts` also sends commentary,
  so it is not a transport fix. `src/playback.ts` and session contracts provide
  useful playing/ended/partial receipts and epoch/turn/hash/expiry fencing. Reuse
  those ownership concepts; do not copy old controller/accounting/media behavior
  or change that repository/Pi. It was not a fresh full-code audit.

## Proposed adapter contract

1. Accept only an app-owned checked utterance: generation/turn, source version,
   language, exact reading and its hash. Revalidate source and checked-parent
   binding before dispatch. No visitor transcript, address, DOB, preferences or
   raw microphone audio enters the renderer.
2. Server-side WebSocket to `/v1/realtime?model=gpt-realtime-2.1-mini` using the
   existing credential/scope. Built-in voice `marin`; no custom voice enrollment,
   new secrets or client API key. Keep the old output route default/disabled
   until the new mode passes its own gates.
3. Wait `session.created`, send/confirm bounded session configuration: PCM16 mono
  24kHz, audio output, no tools, disabled input turn detection, tracing disabled,
   finite token limit. No input audio or conversation history is sent. Request
   one out-of-band `response.create` with `conversation:"none"`, explicit input
   containing only checked text, bounded instructions, `max_output_tokens:1024`
   and an app-generated utterance ID in metadata. Confirm effective settings.
4. Bind `response.created` and every audio/transcript/item event to the expected
   response ID, item, content index and app utterance. Buffer original PCM in
   memory, max20s; transcript<=2000chars; one response, no tools or retries. Hold
   unsolicited/extra/malformed/foreign events, while still settling their usage.
5. `response.output_audio.done` and transcript.done also occur for canceled or
   incomplete responses: they **cannot** authorize release. Require the matching
   `response.done` with `status:"completed"`, complete expected output item and
   transcript, known multimodal usage and no extra output. Never use a quiet pause
   or a request acknowledgment as whole-answer completion. response.done contains
   no raw audio; preserve the received original chunks.
6. Keep the existing whole-waveform independent Transcribe check: exact normalized
   match to checked text, correct language, no supplied transcript hint, unchanged
   source/turn. A renderer transcript match alone is insufficient. Mint no spoken
   approval until all checks and the current-generation fence pass. New model
   name and receipt type must be truthfully bound in server/client validation.
7. Stop/Erase/interruption/language change immediately revoke pending or queued
   audio. Send targeted `response.cancel` with the actual response ID; for an
   out-of-band response, omitting the ID may target the default conversation.
   If cancellation precedes response.created, keep the bounded reader to capture
   its ID and cancel/drain, or retain uncertain usage after the deadline. Never
   dispatch ASR after a known cancel; already-dispatched ASR settles in its worker.
8. Drain canceled/failed responses for terminal usage, then close the renderer
   transport. Realtime does not use Live's `session.close`/`session.closed` protocol.
   No later approval can repopulate the revoked turn. Live input remains a separate
   owner-controlled interaction; native output never leaks through during render.
9. Generation, verified, queued, playing, ended and partially played are distinct.
   Do not tell Live/app context the user heard an answer merely because rendering
   finished. Use application-owned playback receipts, avoid echoing output into
   input, and recheck context after withheld/partial speech. Human media remains
   disabled in current tests; no playing/ended receipt may be fabricated.

Whole-utterance verification still costs time. This correction targets output
fidelity and a real completion boundary, not a guaranteed3s response. First test
one short complete sentence; measure checked-text→first-generated audio→complete
render→ASR→first-approved audio separately. Chunked clauses or warm shared sessions
are later optimizations only if this baseline works and preserve meaning/fencing.

## Accounting and privacy changes required

Realtime uses token pricing, not Live's$0.05/minute stage. Add a distinct ledger
stage with response ID deduplication and actual `response.done.usage`: input/output
text/audio/image tokens and modality-specific cached details. Reconcile subtotals;
reject missing/unknown modes, impossible counts, extra responses or unconfirmed
terminal status. Preserve usage on canceled/failed/incomplete responses even
though their audio is never released. Never price renderer seconds as Live.

Keep Live duration, native Decisions, independent Responses/reviews and ASR separate.
Transport/control attempts are not billable response-usage records: explicitly
record dispatch/acknowledgment and response creation/completion, rather than
fabricating zero usage to satisfy the old attempts==stages shortcut. No existing
unknown native usage or historical ledger row is reset. No unconfirmed terminal
receipt permits another paid stage; retain full reservation and diagnose.

At fetched Oct25 standard rates, Realtime Mini text input/output is$0.60/$2.40 per
million tokens and audio input/output$10/$20; no audio input is planned.1024output
tokens priced conservatively entirely as audio is$0.02048 before input/ASR.
Transcribe is$0.0045/minute. A$.10per-run reserve has margin for one short bounded
utterance but is an application reserve, not a vendor-side dollar guarantee.
Reverify exact model access/rates/effective settings before inference.

Only checked public text reaches Realtime and its generated public waveform reaches
Transcribe. Disable tracing and keep local audio memory-only. Do not copy Live's
`store:false` into Realtime without a supported schema; `conversation:none` is not
zero retention. Official data table lists no Realtime application-state retention
and standard abuse monitoring up to30days; no account-specific ZDR claim is made.

## Necessary unpaid regression groups, before integration

| Owner boundary | Required behavior |
| --- | --- |
| Renderer protocol | Exact response/utterance/item binding; completed versus canceled/incomplete audio.done; missing/late/extra audio; malformed/foreign events; no arbitrary tools. |
| Existing speech release | Real complete buffered waveform, matching declared and independent ASR text/language; changed number/negation/source/turn held; no expected-text bias. |
| Shared cancellation | During rendering, ASR and queued approval; clear buffers/player and reject stale completion; preserve input interaction/context; no human capture/playback from fixtures. |
| Ledger | Deduplicate terminal IDs, include canceled usage, distinct multimodal rates/cached details, unexpected response or unknown finalization stops; transport acknowledgment cannot erase missing model usage. |
| Transcript/UI | Same source/utterance text/language/turn drives captions and allowlisted visual; source original stays labeled; EN→ES→EN preserves context and actual input-caption language. |
| Recovery | Timeout/disconnect/token-limit hold with bounded cleanup, no automatic paid retry or lost accounting; safe text view remains honestly available. |

Reuse/extend existing owner tests at these boundaries, not duplicate every helper
or manufacture a large new framework. Existing whole-waveform/source/revocation
and voice-receipt tests were run and pass during this investigation; they are
reused-contract evidence, not tests of a new Realtime adapter.

## Smallest subsequent paid comparison — proposal for technical review only

Do not reopen/relabel the paused bilingual package. Do not start this plan until
adapter, accounting, fake-transport cancellation proofs and the bounded plan are
reviewed. Existing$200 project authorization is not increased.

- First run: isolated Realtime rendering of the exact already checked English
 120-character text from the failed Live trial, followed by independent ASR.
  No new Live conversation, Responses generation, external tool or human audio.
  Same source pin and actual checked-parent revalidation. One response only.
- Only after a pass: one cancellation run of that same utterance, cancel during
  generation, confirm no approved audio and terminal usage. No second repair slot
  or unchanged retry. Spanish/full native integration are **not** established by
  these two runs and are not silently included in this initial comparison.
- Maximum2runs,5counted dispatch/control operations per run,10total and$.20reserved
  ($.10each) within200. Count connection/configuration/one inference/ASR or cancel
  explicitly; allow only bounded cleanup/drain after a cap, never new generation.
  Request body<=4KB, output<=1024tokens, buffered PCM<=20s, operation<=30s with
  <=15susage/cancel drain, one concurrent run, no automatic retries. Source drift,
  secret/private content, account/rate mismatch, unexpected response, unsupported
  endpoint/configuration, missing usage or tool denial stops the comparison.
- No new credential, access grant, custom voice, paid provider, deployment or
  speaker/microphone permission is included. Confirm model visibility using the
  existing supported account route; if unavailable, report it rather than create
  credentials/grants or switch accounts. Existing retained reserves2.98 would
  become at most3.18 if both runs reserve; that is not an account credit balance.

Technical review of this output-model/event/accounting change is required. No
fresh generic user budget approval is needed solely for work that remains inside
the user's existing OpenAI testing authorization and product scope; normal tool
approval still applies. New credential/access, another provider, private-data
transmission, human media, deployment/merge or exceeding200 would require separate
applicable authority. This proposal grants none of those and starts no paid work.

## Official evidence fetched October25

- [Live delegation](https://developers.openai.com/api/docs/guides/live-delegation#send-the-right-kind-of-update): commentary paraphrases; context acknowledgment is not speech completion.
- [Live playback controls](https://developers.openai.com/api/docs/guides/voice-server-controls?api=live#check-speech-before-playback): app buffering/approval IDs/cancellation, VAD is not complete-answer proof and adds latency.
- [Speech API migration](https://developers.openai.com/api/docs/guides/text-to-speech): legacy shutdown Jan6,2027; Realtime Mini is not a Speech endpoint model.
- [Realtime Mini](https://developers.openai.com/api/docs/models/gpt-realtime-2.1-mini) and [WebSocket guide](https://developers.openai.com/api/docs/guides/voice-websockets?api=realtime): supported model/transport, not account eligibility or fidelity/latency proof.
- [Client events](https://developers.openai.com/api/reference/resources/realtime/client-events#response.create): isolated input, conversation:none, finite tokens, instructions not guaranteed, targeted cancel.
- [Server events](https://developers.openai.com/api/reference/resources/realtime/server-events#response.done): terminal status, transcript/audio event ownership and multimodal usage; audio.done is not necessarily success.
- [Pricing](https://developers.openai.com/api/docs/pricing) and [data controls](https://developers.openai.com/api/docs/guides/your-data): separate token costs/retention, no new account-specific claim.
