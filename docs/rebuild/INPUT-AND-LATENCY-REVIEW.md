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
- **Historical push block:** later resolved only for65bad7a/6d90b11 by exact new
  user approval; see the resolution below. Newer local work remains unpushed.

The next useful measurement is the specifically bounded Spanish brief test.
Microphone input, human heard pronunciation/civic meaning, full generative
composition, all KCEB/JCEB evidence and accessibility/device acceptance remain
separate open gates. Neither a passed local check nor a smaller reading would
make the stretch product ready to share publicly.

## October24 measured optimization and push resolution

Daniel explicitly approved pushing only65bad7a and6d90b11. The remote existing
PR6 head is now exactly6d90b11fc66de4294249bf4cb0e3d89efd3dbd76; both existing
[push](https://github.com/daniel-p-green/open-oracle/actions/runs/40098712545) and
[PR](https://github.com/daniel-p-green/open-oracle/actions/runs/40098709152)
workflows completed successfully. Later commits remain local. The earlier
six-commit approval file is preserved as an immutable historical proposal;
this narrow approval did not approve its full range, Claude upload or paid trial.

Implemented volatile numeric instrumentation: server job queue/routing/retrieval,
Responses generation, deterministic validation, Decisions review, Live audio and
whole-WAV transcription; Live connection/start/instruction/first-last delta/close
and finalization offsets; browser intent/evidence/source/map, checked text,
paint-proxy and prepared-audio readiness. Numbers contain no visitor words,
source history or account identifiers and are not analytics or persistent logs.
Client DOM diagnostics clear on Erase and reject stale writes. Server timings
start at queued job creation; client provider timing also covers admission and
polling overhead. First audio delta is **not** approved/audible speech. Double
requestAnimationFrame is a paint opportunity proxy, not proof that a person saw
pixels. Manual Play/heard speech is not measured.

Parallel local source retrieval was compared with b10c05b plus timing hooks,
using the same retained official map artifacts and simulated150ms question,
350ms geometry and550ms legal-source response delays. Three cold samples each:

| Metric, click to milestone | Serial baseline range | Parallel range |
| --- | ---: | ---: |
| Exact original-source control available |526–539ms|156–163ms|
| Verified maps mounted |526–539ms|367–377ms|
| First useful source paint proxy |545–561ms|163–180ms|
| Complete view, including legal status |1089–1101ms|558–566ms|

One warm parallel sample used cached public question/geometry: source0.4ms,
map mount0.9ms, paint proxy26.2ms; full completion567ms still rechecked legal
status. One normal loopback sample without simulated delay: source14.1ms,
map30.3ms, DOM completion34.5ms, paint proxy42.8ms. These are bounded desktop
observations, not model/Pi/internet percentiles. No response/audio/prerecorded
answer cache was introduced. Numbers and saved-driver verification are in
[LATENCY-LOCAL-2026-10-24.json](LATENCY-LOCAL-2026-10-24.json).

Reproduce source scheduling, with providers disabled:

```sh
python3 experimental/openai-web/research/benchmark_source_latency.py \
  --map-review-dir ../map-review --report /tmp/openoracle-source-requests.json
```

Open8915 for the pinned serial baseline and8916 for current code; choose the same
map example, inspect the current `#workspace` data-view-timing and repeat after
reload. Driver binds loopback only and refuses unavailable ports. Baseline code
is read from Git, instrumented only; no checkout/reset is performed. The saved
driver was actually run. Stop it after comparison. Current ordinary review is
http://127.0.0.1:8917/ with providers off;8914 is an older process/tab and should
not be used as this increment's verification target.

Architecture decision: show admitted source UI immediately; keep concise fresh
Responses text separate from audio preparation. The critical audio dependency
remains text→Decisions→Live finalization→whole-WAV ASR→checked readiness. Existing
33.02s preparation is still the only cited accepted long-reading result; this
increment does not establish faster live speech. The prior26.82s waveform and
31.85s Live elapsed show why a sub3s whole-answer gate is incompatible with that
specific long reading; polling optimization alone cannot remove it.

Next controlled voice comparisons should use a concise complete unit first.
An incremental alternative must compile independently meaningful units, preserving
attribution/negation/conditions/scope, with per-unit source+language+turn+sequence
binding and full actual-audio checks before queue release. A silent gap or a
transcript fragment is not a complete semantic unit. No such streaming release
is enabled now. Original source question/geometry fetches can run in parallel;
review of generated text cannot logically finish before that text exists, and
whole-WAV ASR cannot start before its final waveform exists. No speculative paid
jobs were introduced.

[Official latency guidance](https://developers.openai.com/api/docs/guides/latency-optimization)
supports fewer output tokens, independent parallel work and UI reuse.
[Live client delegation](https://developers.openai.com/api/docs/guides/live-delegation#reduce-backend-latency)
documents persistent connections and coherent verified updates; these are future
provider comparisons, not implemented warming here. Keep provider configuration
stable for caching, inspect reported cache usage, and compare existing Luna
none-effort versus Sol low-effort on the same quality corpus before selecting a
faster model. No model, service tier, timeout, spoken disclosure or independent
ASR gate changed. An explicitly disclosed Realtime2.1Mini synthesis comparison
remains an alternative, not a silent replacement of requested GPT-Live.

Minimal new paid measurement proposal, **not executed/approved**: one English
brief with existing `gpt-6-luna` Responses and independent Decisions, then only if
text passes, same-owner `gpt-live-1` plus finalized-WAV `gpt-transcribe`. Two app
jobs/four requests maximum; reserve≤$0.11 within shared$200, no paid retry,
existing token/duration/timeout/cancel gates and fresh price/account checks before
execution. Record checked text, audio-ready, stage cost and holds; no microphone
or Play. This is conservative application reservation, not vendor-guaranteed
per-request billing. The older≤$0.20 Spanish proposal remains separately gated.
No new trial is needed to reproduce the local rendering results above.
