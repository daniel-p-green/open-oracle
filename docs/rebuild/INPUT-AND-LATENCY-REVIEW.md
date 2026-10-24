# Local input and checked-speech latency — October 24, 2026

This is a bounded implementation increment toward the original stretch journey,
not completion of natural multilingual conversation or public-demo acceptance.

## Implemented and exercised locally

The form drafts supported English/Spanish paraphrases into a fixed public action.
It shows that action for explicit confirmation. The returned draft contains only
kind, operation, language and the application-owned question version. Raw words
stay in the tab and are cleared on confirmation/Erase/idle reset. Contextual
“simpler,” “more detail,” original-source, challenge and recap actions require
an active Proposition A journey. Different measures, arbitrary additions,
political advice and private details do not become model prompts. Unrecognized
wording is honestly unsupported; this bounded grammar is not a general language
understanding claim. Original exact public phrases remain supported.

Typing halts sound while retaining the current checked parent and map. Stop,
Erase, language change and idle reset clear pending confirmation. The async
first-question path checks its session ticket after source loading. Source and
challenge actions reuse the existing controller; confirmation never creates a
second session owner. The initial mapMeasure-not-loaded defect was found in
actual browser review and independently identified, then fixed against the
application-owned version. The independent code review found no further
consequential defect in its scoped pass.

Actual provider-off browser checks: natural first question → map/journey;
Yes/No → typed source follow-up retains the explanation → exact original;
confirmed Spanish switch → Spanish challenge withdraws the explanation and
shows the original; Stop clears a pending follow-up and leaves speakers off.
These are local behavior observations, not comprehension/acoustic acceptance.

A new `brief` operation requests one or two starting sentences and enforces a
260-character limit in Python and browser validation. Its numeric, time,
congressional scope, same-sentence attribution, choice-slot, source-version and
independent Decisions gates remain. Request-fit is critical at the existing .95
threshold, as for overview/limits. Full original, exact Yes/No and more-detail
follow-ups remain available. No disclosure or independent waveform check was
removed to improve latency. The brief operation has not yet had a paid test.

## Existing local Whisper assets and truthful data flow

`local_input.py` is an optional adapter, **not an active microphone route**. It
requires the installed `openai-whisper`20250625 package and an explicitly selected
existing tiny/base/small weight file. The file must match the installed official
model hash before loading by path; no alias fallback/model download is used.
Input is bounded in-memory 16kHz mono PCM16, at most15s. No capture, file write,
logging, cloud call or default model load occurs. Cancellation is checked before
and after native inference; it cannot interrupt that compute mid-call. A future
capture owner must also fence delivery and dispose pending buffers.

The adapter returns text **only for local correction/confirmation**. Local
transcription does not make private content safe to transmit. The existing cloud
boundary continues to accept only public operation/language/source IDs and the
server-owned checked parent. No raw speech/transcript enters Responses,
Decisions, Live, managed Agents or operational receipts. No microphone UI or
browser permission was enabled; no human audio was captured/heard.

All three retained multilingual model hashes verified. With sockets and model
download disabled, using existing public synthetic map-navigation clips:

| Model | Weight bytes | Cold model load | EN inference,8.60s clip | ES inference,11.46s clip | Observed limitation |
| --- | ---: | ---: | ---: | ---: | --- |
| tiny | 75,572,083 | .212s | .328s | .257s | English “maps” became “Naps”; several Spanish word errors |
| base | 145,262,807 | .276s | .499s | .499s | English matched; Spanish imperative phrase misrecognized |
| small | 483,617,219 | .755s | 1.525s | 1.644s | English matched; Spanish “Elija” became “Edija” |

A separate actual adapter check with base and the same Spanish clip took .347s
load/.569s inference, required local confirmation, returned cloud_sent:false and
rejected an already-cancelled input. No audio files were generated or retained
by the adapter. These two synthetic narration fixtures are not natural-question,
accent, noise, accessibility or resident evidence. This is a Mac CPU benchmark,
not Pi throughput or memory proof; process peak memory was not measured. The
installed whisper-cli/ffmpeg and prior OpenAI-only project were inspected, but no
new binary, model or microphone integration was installed.

## Measured latency and architecture decision

The prior accepted English web development run produced26.82s of full PCM,
31.85s Live elapsed and33.02s until checked speech was ready. Approximately1.20s
leading/1.10s trailing low energy was measured. A different run was held on
independent transcript mismatch, so this is not a reliability/percentile claim.
Whole-waveform buffering plus roughly real-time generation makes the reading's
length a dominant delay; reducing request/poll overhead alone cannot reach the
proposed3s conversational target. The target is a product goal, not a vendor SLA.

Retain immediate source-backed text/maps and concise checked answer units.
Measure the new brief answer before choosing a new audio architecture. All
current AI/human-review, personal-scope and explanation-not-quotation disclosures
remain in each canonical reading. Their duration is part of the cost. Do not
claim a disclosure was heard or remove it based solely on preparation.

An explicit future comparison may evaluate approved-text synthesis with
[GPT-Realtime-2.1 Mini](https://developers.openai.com/api/docs/models/gpt-realtime-2.1-mini)
over its documented Realtime endpoint. This would be a disclosed alternative for
synthesis latency, not proof of native GPT-Live behavior or a silent replacement
of the requested stack. Current [text-to-speech guidance](https://developers.openai.com/api/docs/guides/text-to-speech)
says tts-1,tts-1-hd and gpt-4o-mini-tts are deprecated for January6,2027 shutdown;
gpt-realtime-2.1-mini is **not** accepted at `/v1/audio/speech`. No deprecated TTS
integration was added and no new model entitlement/pricing/latency is asserted.

Another option is short independently checked semantic units, with an explicit
application-owned ordered playback queue. That requires evidence that complete
qualifiers and notices survive across units, full actual-audio checks, generation
fences, cancellation and no spontaneous speech. It is not implemented here.
[Live migration](https://developers.openai.com/api/docs/guides/live-migration)
does not allow treating a pending backend result as a global speech pause, and
quiet/co-transcript arrival is not whole-answer approval. The current entire
final WAV remains the independent-ASR release unit. Do not relax that gate to
report a faster result.

## Exact current blockers

- **Paid Spanish measurement denied, known not started:** automatic approval
  review rejected launching a two-job Spanish brief Responses/Decisions then
  same-owner Live/ASR test, at most$0.20 reserved within the shared$200 cap. Its
  stated reason was no user-authored approval for that specific paid run. No
  retry/alternate route. Exact scoped approval question submitted; tool accepted
  it without returning a request ID. Existing ledger unchanged: reservations
  $1.96; recorded usage/duration estimate$0.2127044667 plus earlier unmetered
  Playground usage, not an invoice.
- **New Opus source review upload denied, known unattached:** actual UI selection
  verified Opus5.5High. Eight relevant application source files and review prompt
  were narrowly bundled using installed @steipete/oracle (dry-run/files report,
  render only). Credential/account-pattern scan passed. Automatic approval
  review rejected uploading `openoracle-input-brief-opus55-review.md` to the
  existing authorized Claude chat, saying no trusted authorization for external
  repository disclosure. Attachment count remained0; no submission/retry or
  alternate route. Exact scoped approval question submitted, no request ID.
  Earlier actual Opus reviews remain valid for their earlier scope; none covers
  this new delta. The optional local adapter was not in the denied bundle and
  must be included in its own scope if later submitted for review.
- **Existing PR6 push remains denied/pending Daniel's new approval.** No retry or
  external PR update. Local implementation continues; no remote CI result is
  claimed for unpushed work.

The next useful measurement is the specifically bounded Spanish brief test.
Microphone input, human heard pronunciation/civic meaning, full generative
composition, all KCEB/JCEB evidence and accessibility/device acceptance remain
separate open gates. Neither a passed local check nor a smaller reading would
make the stretch product ready to share publicly.
