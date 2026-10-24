# Pending bounded synthetic voice sequence

**Planning only. Execution is paused after automatic review denied the next
native diagnostic. This document is not authorization or an alternate launcher.**
No run in this sequence has started. Do not retry the denied action until new
applicable authorization is received through the normal review process.

Approval requested: up to **four distinct synthetic OpenAI voice trials**,
**$0.40 aggregate maximum reserved**, at most **$0.10 per trial**, all inside the
existing shared **$200 total**. Current shared reservations are $2.16; this whole
sequence would bring them to at most $2.56. Never treat the unused budget as a
spending target. Skip unnecessary stages rather than consume the allowance.

## Fixed scope

- Use only the already established server-side OpenAI credential and the same
  organization/project account scope as prior successful OpenOracle tests.
  Do not reveal/copy the credential or account identifiers, select a billing
  account, create access, change billing or buy credits. Fresh billing login is
  not technically required for the established credential.
- Models/services: `gpt-live-1` Live session, native `gpt-6-luna` Decisions choices,
  grounded `gpt-6-luna` Responses and independent Decisions review,
  `gpt-transcribe` for independent audio checks. Verify current documented prices
  and these models' availability before execution; stop on changed access/price.
- Only the admitted public Missouri Proposition A source packet and official
  map identifiers. Source version remains
  `09406d86232da1835b4258132ad8eb7c3f22e5098e390fb7b7dcc44f3cec68ec`.
  No personal applicability, campaign excerpt, candidate recommendation or new
  source ingestion. No restricted-source access.
- Caller audio: the existing 4.640s English question about what the referendum
  asks to approve and 3.088s Kansas City map follow-up. Spanish counterparts may
  be generated to files using the already installed local Spanish voice, then
  inspected for format/length/hash. Each clip <=8s, at most two clips per trial.
  Spanish wording: “Escucho hablar de esta pregunta sobre la redistribución de
  distritos. ¿Qué pide aprobar?” and “¿Puede mostrarme esos mapas alrededor de
  Kansas City?” These are synthetic public questions, not a personal profile.
- No human microphone, camera, speaker or playback. Do not add capture/player
  permissions, software, credentials, accounts, remote tools or public hosting.
  No raw private input. Generated output PCM stays in memory and is discarded.

## Stages, each optional after its predecessor

1. **English diagnostic:** brief 120-character answer plus contextual map request.
   Capture only public generated draft/predicate scores, numeric timeline/command
   correlation diagnostics, model choices, checks, final usage and stage offsets.
   Resolve whether the earlier language hold was a genuine mismatch or false
   positive; do not lower thresholds without evaluation evidence.
2. **English verification:** only after a named defect or measured change from
   stage 1 has been repaired/reviewed offline. Verify that repair with the same
   public pair, or skip if no additional live proof is necessary. This is a
   planned post-repair experiment, never an automatic retry of a failed call.
3. **Spanish conversation:** fresh Spanish input, text, source-bound views and
   checked generated speech. Translation/pronunciation/civic quality still needs
   human review; a successful model match is not that approval. Do not send a
   canned English answer with translated navigation and call it Spanish voice.
4. **One recovery experiment:** selected EN or ES pair, interrupt/cancel at a
   documented stage; verify no stale text, map action or audio is released.
   Provider failure/timeout injection is local; no extra paid retries.

## Execution and financial envelope

Each trial reserves $0.10 in the **existing shared ledger before dispatch**. One
Live session, 45s operation timeout plus<=15s graceful close; no more than two
native decision runs, two Responses requests, two independent text-review
requests and two output-ASR requests. If a source-bound input-ASR fallback is
implemented/reviewed, allow at most two additional public-input ASR requests:
**11 total request attempts maximum per trial**, including the Live connection
and native decisions. No tools/sandbox/Agents sessions, web search or background
continuation. Per-response output <=512 tokens and existing 12KB HTTP payload bound.
No output ASR waveform >20s. Nothing is played while an output remains unverified.

At the previously verified rates, 75s Live usage costs $0.0625; bounded Luna text/
review and ASR are additional and expected to fit the $0.10 reservation. This is
an estimate, **not a provider-side dollar hard cap** or an invoice. Transport
cancellation can leave in-flight usage uncertain. Recheck rates; retain the full
reservation and stop the entire sequence if final usage or closure is missing,
reported usage exceeds its bound, cost/account scope is uncertain, or the next
reservation would exceed either sequence or shared cap. No auto-recharge.

A failed semantic/audio check holds that trial and closes the session. Inspect
its public diagnostics and repair offline before considering another explicitly
planned stage; never silently repeat the same request to get a passing sample.
Stop on denied execution, auth/permission request, unavailable model, sensitive
input, source/version mismatch, unexpected extra native run or API expansion.
No alternate route after denial. Preserve each run's code hashes and immutable
receipt before another run so changes and costs can be attributed.

Expected outputs: exact first checked-text/visual-choice/safe-audio and complete
interaction offsets, final input-caption correlation coverage or honest missing
state, current turn/language/source/model choices, independence checks, hold
reasons, bounded cancellation evidence and reported token/duration cost estimates.
Use individual sample values; do not claim p50/p95 or human responsiveness from
this small sequence. Public draft/predicate diagnostics are test-only, outside
Git; operational receipts continue excluding transcripts and voter information.
