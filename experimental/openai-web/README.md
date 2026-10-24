# OpenOracle integrated local review

## Recovered resident journey

The default starting actions now lead to the official Proposition A/map source
journey and candidate-evidence coverage. COMBAT remains an engineering reference.
The connected panel offers fresh overview, simpler wording, more detail and
evidence limits, plus local exact Yes/No effects, source challenge, optional
No-vote teach-back and an ephemeral recap. Source/map browsing stays usable while
generation is pending. Missing optional geometry does not hide the original.

Generation is explicitly enabled server-side; no visitor text is submitted.
The client sends an operation/language and optional parent request ID. The
server retrieves only its own ready same-owner public answer, verifies its source
version and uses that unit as adaptation context. Source and number/time/scope
checks precede separate atomic Decisions judgments. These uncalibrated checks
are not correctness certificates. A real bounded Sol sequence completed English
overview → simpler follow-up → Spanish adaptation from its server-owned prior.
Earlier stricter trials held; separating deterministic sentence attribution,
factual eligibility and requested delivery quality resolved those interface
defects without reducing factual thresholds. Simpler/detail quality can remain
explicitly unconfirmed. Human civic/bilingual acceptance is still pending.

Official U.S. House office passages are independently readable with source/date
and original-English labeling. They establish neither personal district nor
complete candidate coverage. The responsive source/map workspace, optional
teach-back and recap are usable while generation is pending; late results do
not move focus from those activities. See the
[reference/adaptation record](../../docs/rebuild/DEMO-REFERENCES.md).

The existing operator `--max-runs` bound is 1–8 (default1), process-wide, with
global ledger reservations and no automatic paid retries. `--text-model` permits
`gpt-6-luna` (512 output tokens, $0.01 reservation/turn) or `gpt-6.1-sol`
(Low reasoning, 1536 total output tokens, $0.10 reservation/turn). Both have a
12,000-byte serialized request bound, two calls/turn, no tools/background work.
Sol reservations cover conservative input/cache-write/output arithmetic; reported
usage estimates are not invoices. A model comparison is not a winner declaration.

Spanish fresh civic prose/teach-back is held outside explicit local review mode.
That mode permits examination of experimental machine text, not human language
approval. Ready public context lives at most the owner’s ten-minute lifetime;
Erase revokes its references. Missing/expired parent rejects before reservation,
restores the client allowance only on a confirmed unstarted request, and needs a
deliberate fresh action. No automatic retry or prerecorded-answer substitution.

## Fresh per-answer speech — local review only

After a checked fresh explanation, explicit review mode offers **Prepare fresh
voice**. A separate bounded job retrieves that same-owner ready answer; the
browser cannot supply speech prose. It preserves source attribution, quotation
status, human-review uncertainty, unconfirmed delivery and nonpersonal scope.
GPT-Live receives an exact-reading instruction with content delimiters; commentary
is not treated as an immutable approved transcript. Output is buffered until
whole-session finalization. Its transcript and an independent `gpt-transcribe`
pass over the entire final WAV must agree with the canonical reading under a
closed set of pronunciation/typography aliases. Negation and other numbers are
preserved. ASR receives no expected-text prompt or language hint; its primary
detected language must match. Agreement is engineering evidence,
not human pronunciation or acoustic approval.

The existing job/budget/session/SpeechOutput owners manage this path. Each
speech run reserves $0.10 and permits one Live session plus one ASR request,
no retry. The web job rejects a reading estimated over45s (12characters/sec)
before reservation; that heuristic is not a duration guarantee. Live has a52s
generation bound and90s transport timeout, client115s,
accepted final usage≤75s, PCM≤60s and ASR HTTP timeout20s. Duration-based price
arithmetic at those accepted bounds is $0.067; uncertain or failed work retains
the whole reservation. These application bounds do not promise a provider-side
spending cap or refund. A complete planned co-transcript plus a quiet interval
can trigger session close; it never approves release. The full final waveform
still goes to ASR, without trimming quiet words. Full-answer buffering is a
**known latency limitation**, not the natural/low-latency release experience.

WAV access requires the owner-token header and ready child+parent. Parent
revocation/expiry clears dependent speech; audio expires120s from ready with a
hard240s cap from request and the owner's expiry.
Cached browser media has the same lease, checks server readiness before manual
Play and rechecks sufficient lease for the clip duration+2s after that asynchronous
validation. Same-parent source/map browsing pauses playback and preserves
preparation. Stop/Erase/Challenge/language/parent changes revoke it. Expired audio
has an explicit state and never causes automatic regeneration. There is no
automatic sound or microphone.
Fresh speech remains review-only pending human approval.

**Verified:** local provider fakes, ownership/cancellation/expiry checks, server/
browser EN/ES reading parity, actual English Live+whole-WAV ASR adapter and web
preparation. A real missing disclosure and a later ASR disagreement were held.
The instrumented public-only web run prepared26.82s of audio in33.02s; no sound
was played. These few development runs do not estimate reliability. Actual
Opus5.5High critique/re-reviews returned. The earlier approval denials were
resolved on newly supplied authority, with one permitted retry each.
**Not verified:** human-heard sound, Spanish fresh speech, civic/bilingual/
acoustic quality, natural private-safe spoken input, accessibility acceptance or
whole-product readiness. See logs.md for actual costs and failure evidence.

The candidate pane now includes all three printed U.S.House District5 candidates
and write-in from the pinned KCEB W1-P7 public sample, with page/field provenance
and equal background-evidence gaps. It is not a complete KCEB/JCEB inventory or
personal ballot. Office context is sourced independently; names alone never
merge records or establish a candidate's position.

**Not the completed multilingual voice/generative-UI product.** This is a working
local evidence workspace with prepared synthetic narration, not a human voice
trial or public-release approval. Python **3.12+**; no project Node dependency.

From the repository root:

```sh
python3 experimental/openai-web/server.py
# http://127.0.0.1:8894 — providers off, unreviewed audio and diagnostics hidden
```

The current retained local review assets live outside Git. With those assets:

```sh
python3 experimental/openai-web/server.py --port 8899 \
  --map-review-dir ../map-review --experience-dir ../experience-review --review-tools
# http://127.0.0.1:8899
```

`--review-tools` deliberately exposes old diagnostics, standalone map review,
silent lifecycle exercise and unheard synthetic audio for local review. It does
not grant microphone or speaker consent. **Do not activate Play without the
person's explicit consent.** Default mode filters clips with
`acoustic_human_review:false`. The server binds only to loopback; do not expose it
as a public service. No API key is read without explicit provider enablement.

The workspace offers source-backed COMBAT facts/Yes–No effects, exact originals,
coverage/refusal/unknown-membership states and the actual paired official map
artifacts. Unknown paraphrases require selecting a topic; a different measure or
jurisdiction is never silently converted to COMBAT. English/Spanish interface
and map navigation work; Spanish civic explanations remain held for human
review. The official KCEB Proposition A wording is a pinned **public sample**,
not personal-ballot applicability. Court/docket status is a separately pinned,
dated record with a review deadline; stale/missing status is withheld.

Prepared public voice clips are matched to language, intent, source version,
text and byte hash. Reset/Stop/language/source changes fence delayed results;
playback requires separate speaker consent and a deliberate Play. Captions show
the prepared transcript, not live human captions. Full model transcript checks
and independent ASR are not human pronunciation or acoustic review. No human
microphone path is enabled; camera/geolocation/microphone permissions are blocked.

## Bounded provider experiment

Only an operator with already authorized API access may enable providers:
Python environment with pinned `requirements-provider.txt`, existing process
`OPENAI_API_KEY`, explicit organization/project scope, private existing authorized
ledger and `--enable-openai --max-runs 1` (maximum8). Keep account values, keys,
ledgers, audio and receipts outside Git. No credentials/access are created here.

Baseline content is immediate and local. The optional button runs a single
`gpt-6-luna` Responses check choosing card order from fixed options; this is a
narrow generative-UI experiment, not broad UI generation. It sends only a canned
intent ID, never the raw typed question. Unknown/candidate one-order recipes and
language switches do not spend a model run. Request/body/poll timeouts, bounded
schema/output, owner token, idempotence/cancel tombstones and shared conservative
reservations apply. Cancellation suppresses later stages/results; an in-flight
HTTP request can drain to its transport timeout and may still be billed.

The review-only `/diagnostics` retains the earlier fixed rate pipeline: Decisions
routing → exact Responses claim selection → Decisions support check → buffered
GPT-Live preparation. Live buffers are checked at complete session close; no
per-spoken-response completion event is assumed. Its PCM remains in server
memory with a two-minute TTL and no download/playback route. This is distinct
from the intentionally retained prepared synthetic WAV fixtures above.

## Verification and review

```sh
node --test experimental/openai-web/tests/*.test.mjs
python3 -m unittest discover -s experimental/openai-web/tests -p 'test_*.py'
```

These checks use fixtures/mocks/local HTTP, not paid services or microphones.
CI uses pinned official Actions with read-only permissions and no model secrets.
Check remote status separately. See [acceptance](../../docs/rebuild/DEMO-ACCEPTANCE.md)
and [actual independent review/dispositions](../../docs/rebuild/CLAUDE-REVIEW-2026-10-24.md).

## Rebuilding private retained assets

Map originals and derivative are outside Git. Supply the exact four filenames
and versions in `docs/rebuild/MAP-SOURCE-MANIFEST.json`:

```sh
python3.13 -m venv ../.map-venv
../.map-venv/bin/python -m pip install -r experimental/openai-web/research/requirements-maps.txt
../.map-venv/bin/python experimental/openai-web/research/build_maps.py --inputs ../map-research --output ../map-review
```

A derivative must match the independently reviewed application pin. Changes
require review and explicit repinning. Geometry checks do not prove absence of
all holes, quantify political changes or clear state reuse rights. A verified
accessible territorial description is still unavailable; district-number tables
are not an equivalent geographic explanation.

The offline one-candidate research compiler is retained:

```sh
python3 experimental/openai-web/research/build_evidence.py --inputs ../evidence-research --output ../evidence-review
```

It uses pinned official filing/attributed campaign excerpts for local review,
not a nationwide connector or publication approval. Managed Agents is deferred;
see [exact budget limitations](../../docs/rebuild/AGENTS-BUDGET-REVIEW.md).
