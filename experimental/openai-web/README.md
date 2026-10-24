# OpenOracle integrated local review

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
ledger and `--enable-openai --max-runs 1` (maximum2). Keep account values, keys,
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
