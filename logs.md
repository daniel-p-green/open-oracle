# OpenOracle rebuild decision and action log

This file records project decisions, actions and evidence. Status words are
**completed**, **running**, **planned** and **blocked**. Costs are estimates unless
explicitly identified as invoices. Operational credentials, account identifiers,
private transcripts and voter information do not belong here.

## Backfill recorded 2026-10-24 UTC

The entries below reconstruct this rebuild from retained task history, documents
and Git. Times on commit entries are the original Git author timestamps; other
events lack retained precise timestamps and are deliberately not assigned one.
This is a backfill, not a contemporaneous event stream.

- **Completed — discovery:** preserved the original dirty `feat/semantic-retrieval`
  checkout at `1ba756d`; created an isolated rebuild from verified public remote
  main `c5d9180`. Reviewed Hack Midwest post-mortem and source/claim contracts.
  Useful product, provenance, cancellation and accessibility work survives.
  Hosting access blocks and unfinished integration are evidenced; no claim that
  every failure was caused by Amazon. No unrelated PR or original work changed.
- **Completed — direction/approval:** Daniel requested OpenAI-native web-first,
  later Pi, specifically GPT-Live and Decisions, and clarified the Amazon
  architecture was wrong. Parent remains project lead. Read OpenAI docs and
  codebase-design skills; exact requested software-engineering skill was not
  found. Official docs verified actual services/endpoints before implementation.
- **Completed — 2026-10-23T21:14:09-05:00, `42bc00b`:** recorded discovery and
  [architecture decisions](docs/rebuild/DECISION.md). Retained a finite public
  COMBAT sample as harness; personalized official ballots alone establish
  membership. No DOB/address/private voter records, advice or profiling.
- **Completed — 2026-10-23T21:20:54-05:00, `e9e6fd3`, and
  2026-10-23T21:22:18-05:00, `86a5cce`:** runnable provider-off local web slice,
  visible exact sources/uncertainty, candidate/office and membership abstention,
  Spanish civic hold, keyboard/reset/idle flow. Initial evidence: 10 Node and
  five HTTP tests passed; browser source, narrow viewport and reset exercised.
  No Pi/display-device or screen-reader acceptance claimed.
- **Completed — project publishing approval:** Daniel requested consistent
  meaningful commits/PRs. Verified repository identity/visibility and ownership;
  opened draft [PR6](https://github.com/daniel-p-green/open-oracle/pull/6).
  This superseded the earlier repository-publishing hold, not deployment limits.
- **Completed — 2026-10-23T21:25:59-05:00, `2719937`:** independent review found
  source mutation during asynchronous validation. Snapshot/freeze fix plus
  mutation regressions protect admitted text and citations.
- **Completed — 2026-10-23T21:40:35-05:00, `92befe1`:** explicit simulated mic
  consent, active state, manual silent playback, interruption/reset and complete
  reading receipt contract. Fixed audio-metadata mutation and changed-question
  invalidation; later added actual app-event locale/load-race regression.
- **Completed — API approval and account verification:** Daniel authorized at
  most $200 shared testing spend, not a spending target. Read-only official
  Platform balance verified sufficient existing API credit; auto-reload remained
  off. Existing process credential used only server-side with explicit account
  scope. No key creation/extraction, billing change or expanded access.
- **Completed — 2026-10-23T21:45:58-05:00, `db0cdbe`:** recorded independent
  fixes and five bounded paid smoke requests: two Decisions Playground controls,
  one Responses draft, one Decisions support check and one synthetic-input Live
  session. Direct metered estimate about $0.00843 excludes two UI requests whose
  charges were unavailable; $0.30 conservative reservations. No invoice or
  population accuracy claim. All three requested services actually responded.
  See [receipts summary](docs/rebuild/CONSENT-AND-API-CHECKPOINT.md).
- **Completed — audio architecture decision:** official Live docs say backend
  waiting does not pause all speech and commentary may paraphrase. Therefore
  buffer all output and full transcript until graceful session close; exact
  approved reading/currentness checks precede release. No exposed spontaneous
  audio, microphone or speakers. Rejected tool-return timing as a safety gate.
- **Completed — 2026-10-23T22:06:14-05:00, `eb1b678`:** integrated explicit
  server-enabled Decisions → constrained Responses → Decisions → buffered Live
  path. Fixtures remain default. Fixed public question only; no visitor text
  sent. Private spend reservations, ownership, timeouts, cancellation tombstones,
  no secret/audio routes and two-minute memory expiry. Added pinned read-only
  public CI workflow with no credentials or paid calls; remote execution pending.
- **Completed — initial integrated attempt:** held at routing, no answer/audio
  released. One Decisions request used 140 input tokens: estimated $0.000014.
  A separately reserved diagnostic confirmed `abstain` (0.59 probability;
  confidence 0.18), same tokens/estimated cost. No blind downstream retry.
- **Completed — source-policy correction approved by owner:** candidate evidence
  only from official filings/records, attributed official campaign statements
  and original debates/verified transcripts. Newsroom/VGC candidate evidence
  rejected. All official roster candidates stay visible through coverage gaps;
  no name-only merges or missing-evidence position inference. Rights restrictions
  hold MEC finance ingestion and unauthorized caption downloads.
- **Completed — hybrid direction approved by Daniel:** application owns durable
  corpus, rights, identities, effects ledger, versioning and publication gates.
  Trial Agents API for one bounded asynchronous bundle; SDK remains an alternative.
  No SDK/API double framework or researcher swarm. Sessions persist and are not
  ZDR eligible; no personal voter data. Trial eligibility/pricing/rights must pass.

## 2026-10-24 UTC — current milestone

- **Completed:** read/check found no existing root `logs.md`; created this
  explicitly labeled backfill at Daniel's request. Future meaningful milestones
  will update this file with related commits.
- **Completed:** repaired route instructions to distinguish lookup classification
  from answering/source sufficiency; retained confidence threshold and exact
  admission gates. Added safe outcome reason visibility without provider payloads.
- **Completed:** 38 Node tests and 29 Python tests pass. Default sandbox denied
  ephemeral HTTP bind; reviewed local execution succeeded. Independent reviewer
  previously verified cancellation-at-entry, overflow-final-usage and expiry
  fixes; later owner regressions added route contract and client expiry checks.
- **Completed:** drafted [primary-source architecture and acceptance plan](docs/rebuild/PRIMARY-SOURCE-ARCHITECTURE.md),
  including retained Hack Midwest components, source classes, identity/rights,
  incremental ingestion, correction invalidation and bounded hybrid trial.
- **Running:** one corrected, reserved integration check; outcome must be logged
  before claiming a working real end-to-end result. Reservations before it total
  $0.45, including the diagnostic. No invoices confirmed.
- **Planned:** push focused updates to PR6 and inspect actual CI; then perform
  the agreed bounded evidence-bundle trial only after account/rights preflight.
- **Blocked by explicit scope:** human mic/speaker journey awaits device and
  utterance consent. No public deployment, Pi modifications, new credentials,
  bulk transcription, purchases or expanded access are authorized.
