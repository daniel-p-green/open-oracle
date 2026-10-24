# Bounded evidence and official-map checkpoint — October 24, 2026

The first deterministic official-map comparison runs locally. The candidate
primary-source bundle compiles offline, with attribution and gaps. **The paid
Agents API trial stopped before session creation:** a $5 reservation alone is
not an enforceable remote spending limit.

## Actual local artifacts

- `/maps` on the explicitly configured loopback review server shows paired 2022
  and proposed HB1 geometry, synchronized statewide/Kansas City/St. Louis views,
  numbered selection and an accessible district table. Both panels share
  EPSG5070, bounds, scale and neutral styling. No location, external tiles,
  demographic/partisan claims, microphone, audio or AI generation.
- Originals and derivatives stay outside Git. The [source manifest](MAP-SOURCE-MANIFEST.json)
  pins all four originals. The [application derivative pin](MAP-DERIVATIVE-PIN.json)
  binds the actual reviewed 2,788,006-byte result; a file's own receipt cannot
  authorize invented geometry. Source data/geometry are not published by this PR.
- Actual build verified eight IDs per plan, valid original/projected geometry and
  coverage edges, without simplification. It does not prove no holes, survey
  precision or political change classification. [Shapely coverage validation](https://shapely.readthedocs.io/en/2.1.2/reference/shapely.coverage_is_valid.html)
  permits holes; [pyproj's transformer](https://pyproj4.github.io/pyproj/stable/api/transformer.html)
  reports the chosen conversion accuracy (4m for proposal WGS84→NAD83 here).
- Actual browser checks exercised state/KC/STLouis, matching district selection,
  Tab/Enter, source/version notes and narrow stacked layout. At 320px there was no
  horizontal overflow. No screen-reader/Pi/bilingual acceptance is claimed.

The September 25 stay preserves the 2022 map for November 2026, not final resolution
of every challenge. The latest Missouri cd120 GIS remains unsuitable as current
truth until Census's correction. See [legal/freshness references](PRODUCT-ROADMAP.md).
Public distribution does not establish all state-map reuse rights; this is local
review, not a license determination or public deployment.

## One candidate bundle, precisely scoped

Retained three exact originals, retrieval timestamps and hashes: an independent
[FEC Form 2 filing](https://docquery.fec.gov/pdf/614/202606219874229614/202606219874229614.pdf)
for candidate ID H4MO05234, plus the campaign's
[issues](https://www.cleaver4congress.com/issues) and
[identity](https://www.cleaver4congress.com/about) pages. FEC's own candidate page
linked that filing. No donor records were collected. Full originals/extractions
and the compiled bundle remain local; no candidate research draft is published.

The bundle retains source class, claim role, publisher, original/extraction hash,
document date or explicit unknown, retrieval time and exact page/code-point span.
A campaign statement remains an attributed claim, a filing remains a filed
assertion. Identity review is limited agent research, with human approval pending.
Reuse permission is limited to the local short-excerpt review; no blanket license
or external-model permission is inferred. Publication is disabled.

Two direct Missouri SOS downloads returned HTTP 403 and were not retried through
another route: the [general-election candidate certification PDF](https://www.sos.mo.gov/CMSImages/ElectionCandidates/2026GeneralElectionCertifiedCandidates.pdf)
and [primary filing-register page](https://s1.sos.mo.gov/candidatesonweb/DisplayCandidatesPlacement.aspx?ElectionCode=750006905).
Their indexed discovery text is not admitted as a retained
original. This independent federal filing does **not** establish Missouri ballot
membership or replace the unavailable SOS versions. No rights-cleared debate
transcript was supplied/admitted; that class is explicitly missing. No captions
were downloaded and no transcription or voice input occurred.

## Exact paid-trial blocker

Read-only Agents project access previously returned HTTP 200. Current official
[session documentation](https://developers.openai.com/api/docs/guides/agents-api/sessions)
provides an asynchronous cancel event; it does not establish that closing the
client stream stops work. No per-run hard spend/token cap was verified in the
inspected [create-session schema](https://developers.openai.com/api/reference/resources/beta/subresources/agents/subresources/sessions/methods/create).
The official [Responses spending controller](https://developers.openai.com/cookbook/articles/per_run_spending_controller_responses_api)
explicitly excludes server-managed agent runs; project alerts/limits cannot be
assumed to stop immediately.

If create times out before a session ID arrives, or cancellation acknowledgement
is lost, local timeouts cannot demonstrate remote stop or bound remaining billing.
The application therefore has **no enabled paid Agents dispatcher**. No creation
request, model inference, hosted sandbox, credential/access change, spend or new
reservation occurred in this milestone. Existing shared reservations remain $0.55;
previous metered estimates are unchanged. The requested at-most $5 trial ceiling
remains a gate, not a claim that a remote cap exists. No automatic retry.

A small durable local effects ledger proves logical-job idempotence across reopen,
rejects changed-payload reuse, distinguishes Stop from confirmed cancellation,
prevents redispatch after uncertain outcomes, and retains a late matching session
ID for cancellation without resuming work. This is offline behavior, not remote
exactly-once or cancellation latency evidence.

## Proportionate proof and remaining work

Focused source checks reject changed originals/spans, foreign candidate identity,
newsroom evidence, claim-role promotion and path/rights violations. A narrow
map regression rejects an invented derivative despite copied official metadata
and a self-matching receipt; real source/geometry build proof is recorded
separately. Existing source/audio/privacy/currentness gates remain passing.
Independent review found and verified repairs to derivative authority and late-ID
recovery. Counts are execution bookkeeping, not model-quality statistics.

The actual credential-free [remote CI run for `518faf2`](https://github.com/daniel-p-green/open-oracle/actions/runs/40059695820)
completed successfully. GIS execution/visual checks were local; this workflow
checks offline contracts and syntax, not map rights, actual remote cancellation
or model quality.

Used the installed `test-audit` guidance and its pinned OpenClaw provenance;
inspected `@steipete/oracle`, which is a bundling skill rather than an anti-testing
rule. No separate named Peter/software-engineering anti-test skill was found.
No external Oracle submission. OpenAI Docs and Evals guidance keep documented
capabilities, source admission and future generation-quality evaluation distinct.

Next: resolve a verifiable managed-run cost/stop envelope before Agents inference;
review candidate identity/quotes/rights before publication; review the map's exact
measure/version association and reuse scope before broader integration. Keep
human mic/speaker, Spanish civic release, public deployment and Pi changes held.
