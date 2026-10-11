# Reviewed research release and local source bootstrap

Updated October 11, 2026. Local implementation and fixed public-source trials; no publishing, media capture or playback.

## What was repaired

The real multi-part research failure was a source contract error, not proof that the question lacked evidence. The model retyped a PDF quotation with different line breaks and cited a chunk read for the rate part to support duration. `read_evidence_chunk` now issues a raw citation span ID for each eligible bounded chunk **and each part**. The ID resolves to request-owned original text. Exact quotations, original/extraction/chunk hashes, Unicode offsets, authority, election, source role and scope remain enforced. Legacy normalized quotations, forged IDs and cross-part reuse still fail closed.

`research_reviewed` is a dependency-injected, text-only core service. The agent substantively plans independent parts, searches the approved registry, acquires hash-checked retained originals, ranks chunks with SQLite FTS5 and reads each part. The release adapter accepts only two finite, source-bound COMBAT proposal explanations: rate and duration; an unsupported crime prediction receives an explicit evidence-gap refusal. A narrow independent intake check rejects unrelated or dropped requests. Broad/legal/generated research remains private. This is not arbitrary prose entailment, a general legal explanation engine, a browser research switch or a speech route.

After model completion, core rebinds the entire draft, plan and citations, checks the printed proposal grammar and qualifiers, then invokes independent Decisions review with the unchanged 0.95 threshold. It rechecks source binding and cancellation after review. The final content-free receipt follows these checks; cancellation clears release metadata even if a candidate answer was accepted moments earlier. Release configuration, tool code, schema and source pins are hashed. A receipt or citation is execution evidence, not factual-quality approval. Decisions remains fallible and its threshold uncalibrated.

## Actual live evidence

All calls were separately reserved in the shared $50 ledger, using the existing permitted integration. No silent retries, voice, recording or playback.

| Fixed fixture | Real Strands calls | Real Decisions calls | Actual outcome |
|---|---:|---:|---|
| Diagnostic research failure | 6 | 0 | Held: non-exact quote; duration part had no read |
| COMBAT rate and duration | 6 | 1 | Released two source-bound claims; all required model estimates ≥0.99 |
| COMBAT crime reduction by 20 percent | 4 | 1 | Released explicit unsupported-prediction refusal, zero factual claims |
| Reading level, initial diagnostic prose | 5 | 1 | Held: source checks passed, Decisions clarity 0.38 |
| Reading level, clearer prose and no unrelated card | 5 | 1 | Held: source checks passed, Decisions clarity 0.28 |

The successful research answer was: “The question proposes continuing the COMBAT tax at a rate of one-quarter of one cent. The question proposes continuing the COMBAT tax for ten years.” Both claims cite separate part-owned reads of the retained JCEB question, original SHA-256 `032814e650dbdbdb0064acb396ead6f51dcd087778240802eb6c30c7a5ef64a2`. No derived percentages or economic/legal consequences were generated.

The refusal was: “The retained ballot wording does not establish whether COMBAT would reduce crime or by how much. I cannot support that prediction from this evidence.” Its receipt shows `plan_evidence`, source search, `record_source_gap`, and final schema execution. It does not invent a supporting source.

The requests/tool events, token usage, source hashes/quote offsets and review results are in `evals/release-repair-20261011/`. These are fixed test questions and public evidence, not visitor transcripts. The live trials preceded a subsequent strengthening of the independent intake guard and release-config/late-cancellation metadata; those later boundary changes passed offline SDK regressions, without repeated paid trials. Do not claim the final code hash itself received another live run.

Total shared allocation at this checkpoint: **$10.40**, with **$39.60 unallocated**. These are reservations, not an invoice or confirmed spend. The retained ledger remains local and excluded from Git.

## Readability boundary

Explicit reading-level requests now receive a finite diagnostic explanation rather than the generic COMBAT overview. The complete retained question, including the separate trust-fund condition, is scored and rebound. Every report field is independently recomputed from the scoped original before release; altered counts, scores, method, raw-text hash, span or answer fail closed even if a reviewer would accept them. Original quotations are preserved. Diagnostics never become speech or factual-fidelity/comprehension/voting-advice gates.

The exact-source local diagnostic works, with independent model review clearly marked not run. The live diagnostic remains withheld after both clarity rejections. A lower threshold, excluded clarity criterion or passing result has **not** been substituted. Whether the revised prose and school-grade interpretation are suitable needs independent clarity/comprehension validation; these two calls do not establish quality-check reliability. The ordinary COMBAT original-wording fallback stays available.

## Fresh checkout source bootstrap

The repository intentionally excludes the full research archive and `.local/sources`. Import the supplied inspected files explicitly; startup never downloads or replaces them:

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m open_oracle.bootstrap_sources \
  --research /absolute/path/to/HackMidwest2026_research \
  --prepared /absolute/path/to/existing/.local/sources
.venv/bin/python -m open_oracle
```

`--prepared` is optional; omitting it leaves candidate-position comparison as an explicit gap. `--check-only` validates the supplied files without copying. The bootstrap imports only 25 pinned runtime research files, including permitted current-cycle judicial originals, plus the optional two prepared candidate files. It verifies all source bytes and candidate passages before writing; rejects symlinks/path escapes, missing/changed evidence and existing destinations; uses ignored local staging; never edits supplied originals, configures credentials or fetches from the network. Installation exposes each validated archive by directory rename; the pair of research/prepared directories is not a cross-directory transaction.

Actual local import reconstructed 55 contests, 62 candidate names, 11 retention questions, ten measures, four research sources/99 chunks and four attributable candidate answers. Fresh-checkout validation reuses the already installed pinned dependency environment; it is not proof of a clean-machine dependency install. Source redistribution and another GitHub push remain unapproved.

## Visual integration

The reviewed America.gov patch is integrated in `web/index.html`, `web/styles.css` and `web/app.js`. It preserves the entire original, marks one exact selected clause and places its explanation underneath. Accepted static speech text remains separate and unchanged by clause navigation. The explicit local body faces select HelveticaNowText-Regular/Medium, then Arial, avoiding this Mac’s installed Black-family collision. No font binary is copied, downloaded or hotlinked; exact reference webfont licensing is unresolved.

Source/privacy/voice/input/orb/Copilot transport ownership is preserved. Physical Pi rendering, actual audibility, aligned captions, multilingual delivery and camera/wave accuracy remain unverified. Gesture research is separate staging; no new gesture implementation or device capture was enabled here.
