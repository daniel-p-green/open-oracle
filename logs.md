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
- **Completed:** corrected integration run reached ready through all four real
  stages. Actual browser showed exact source-bound rate, citation and sample
  uncertainty; 925,440 PCM bytes, full matching transcript, final usage 19s.
  No playback/mic. Successful-run usage estimate $0.0159354; all direct metered
  estimates total $0.0243915 plus two unexposed Playground charges. Conservative
  reservations $0.55. No invoices confirmed. Paid inference stopped here.
- **Completed — new owner direction:** multilingual fact-based voice and
  source-backed generative UI, including actual official current/proposed maps.
  Added [integrated roadmap](docs/rebuild/PRODUCT-ROADMAP.md) with typed evidence
  components, bilingual review/acceptance and accessible Pi-aware rendering.
  Read-only SOS discovery identified HB1 reference 2026-R004 on a circulation
  page; exact certification, map versions and legal operation remain unverified.
  No map admission, drawing or district inference occurred.
- **Completed — freshness follow-up:** independently read the Sept25 Supreme
  Court opinion, Sept10 SOS statement and Census product notice supplied by the
  parent. 2022 boundaries govern the 2026 election; latest Missouri cd120 GIS is
  not yet regenerated. Roadmap now prohibits using file recency as map authority
  or describing referendum effects as changing an already-used 2026 ballot.
- **Completed — Agents API preflight:** documented read-only sessions request
  returned HTTP200 in the existing scoped project. No inference/session created,
  no new key or permissions. Read access alone does not establish write/model
  eligibility. Quickstart/manage docs are available; linked reference pages
  returned404 through the docs fetcher; official HTML reference subsequently
  loaded. No documented per-turn token/spend cap was found in the inspected
  create-session schema. Bounded inference controls and source-bundle admission
  remain prerequisites; no parameters or API permissions were invented.
- **Completed — published milestone:** pushed `eb1b678`, `46298f0` and `f61102b`
  to existing draft PR6 and rewrote its description around actual integrated
  behavior, evidence and primary-source limits. No merge/deployment.
- **Completed — remote verification:** GitHub Actions
  [run 40058014545](https://github.com/daniel-p-green/open-oracle/actions/runs/40058014545)
  for `f61102b` completed successfully; inspected job steps confirm JavaScript,
  Python loopback/provider mocks and syntax/whitespace checks passed. No model
  credentials or paid calls in CI.
- **Completed — independent review at `f61102b`:** reviewer reran 38 Node and
  29 Python tests plus syntax/diff checks, with no new substantive current-code
  finding. Route classification retains .95/source/review gates. Current safe
  reason codes do not expose provider payloads; the lexical UI filter is not an
  enum and needs reassessment for future adapters. Review did not independently
  inspect private receipts or court/map sources and made no paid calls.
- **Planned:** agreed bounded candidate evidence-bundle trial follows source
  identity/rights admission and a verified cost/cancellation envelope. Read access
  is verified; write/model operation remains untested. No Agents session created.
- **Completed — 2026-10-24T03:24:14 UTC map research downloads:** parent supplied
  verified official baseline/proposed pair and OA distribution chain. Downloaded
  four exact URLs under 16MiB/file, 20s/request bounds and pinned SHA256 hashes in
  [research manifest](docs/rebuild/MAP-SOURCE-MANIFEST.json). Confirmed proposed
  GeoJSON has eight IDs1–8/EPSG4326; baseline PRJ is NAD83 degrees. Originals stay
  outside the public repository. No topology, rendered comparison or blanket
  reuse license claimed. State-source rights, exact ballot/version admission and
  final legal freshness remain gates; stay is not final resolution of all cases.
- **Blocked by explicit scope:** human mic/speaker journey awaits device and
  utterance consent. No public deployment, Pi modifications, new credentials,
  bulk transcription, purchases or expanded access are authorized.

## 2026-10-24 UTC — bounded evidence and official-map review

- **Direction:** parent authorized the next single primary-source evidence-bundle
  trial, with at most $5 reserved within the shared $200 ceiling, only after
  cancellation and hard stopping are verified. Separately authorized a local
  deterministic side-by-side official map review. No mic/speaker or deployment.
- **Completed — official API check:** reread Agents session/cancel/create schema
  and official per-run spending-controller guidance. Managed turns are async;
  closing a stream is not proof of stopping the server. No verified per-run hard
  token/spend limit was found; cancellation can be unconfirmed if the initial
  create outcome/session ID or cancel acknowledgement is lost. The documented
  Responses spending controller explicitly excludes server-managed agent runs.
- **Blocked before paid dispatch:** no Agents session/create/inference request
  was sent. No new spend or reservation; prior conservative reservations remain
  $0.55. The $5 ceiling is not treated as enforceable merely by reserving money
  or using a local timeout. This is an unresolved capability guarantee, not an
  API denial or a request for new credentials. Local preflight remains closed.
- **Denied, not retried:** direct downloads of the SOS general-election
  certification PDF and primary filing-register HTML each returned HTTP403.
  Original bytes were not retained. Indexed discovery text is not admitted
  evidence. No alternate retrieval, header trick or access expansion attempted.
- **Completed — independent federal source:** followed FEC's candidate page to
  current Form2 filing `FEC-1986179`, June21, 2026. Retained the exact PDF and
  retrieval timestamp; SHA256 begins `82c0b49b0949eb68`. This distinct official
  filing supports federal identity/filing fields, not Missouri ballot membership.
  No donor records collected; original and full extraction remain outside Git.
- **Completed — campaign source capture:** retained the exact campaign issues
  and about HTML with retrieval times/hashes. Built a local-only bundle with one
  short attributed campaign excerpt, FEC identifier span and campaign identity
  span. Full name, filing ID/office/year/committee and campaign self-identification
  inform the limited review; independent human approval remains pending. No
  assertions promoted to established facts; no model or public release.
- **Completed — offline bundle:** verified original/extraction hashes and exact
  code-point spans for three source documents. Preserved document date or explicit
  unknown, publisher, locator, claim role and local-only rights scope. Debate
  transcript explicitly missing; no unauthorized captions or transcription.
  Repeated logical prepare reuses the stored submission identity. The durable
  effects ledger rejects changed-payload reuse and redispatch after uncertain
  creation or Stop; cancel request and confirmed cancellation are distinct.
  These are local behavior checks, not proof of remote exactly-once execution.
- **Completed — deterministic map build:** four originals verified; both eight-
  district coverages and projected geometry valid, with valid coverage edges.
  EPSG5070, same bounds/scale/style for each paired view, no simplification;
  display coordinates rounded to 0.1m. WGS84→NAD83 conversion reports 4m accuracy.
  Derived local JSON is 2,788,006 bytes, SHA256
  `68b3dec613d58653a64337001bd66b3fa33b18f2184845bd15ad4fdbacde4c25`.
  No change-area/demographic/partisan inference; shoreline slivers not classified.
- **Completed — local visual workflow:** served on loopback port8895 with
  providers off. Actual browser showed paired official maps, source hashes and
  legal/version/rights limitations. Statewide/KC views and district5 selection
  synchronously changed both panels; DOM inspection confirmed identical SVG
  viewBoxes, one selected district per panel, no media elements or desktop overflow.
  Improved label size after visually inspecting the regional view. Narrow viewport,
  keyboard and StLouis checks are the remaining visual acceptance checks.
- **Direction/skills:** Daniel explicitly requested appropriate skills including
  the Peter Steinberger one, with proportionate meaningful testing. Located/read
  actual installed `test-audit/SKILL.md` and its provenance/writing-tests guidance:
  locally adapted OpenClaw skill pinned at `3260cae2`, not an individually verified
  Peter-authored file. Also read installed `oracle/SKILL.md` (`@steipete/oracle`);
  it concerns review bundling, not an anti-testing rule. No external Oracle run or
  bundle transmission. Searched installed skill/plugin roots; no separate named
  Peter/software-engineering anti-test skill found. OpenAI Docs and codebase-design
  remain consulted; Evals routing/evaluate-rag distinguishes source admission from
  generation quality. No synthetic metric or authored fixture count is a quality claim.
- **Test-audit application:** retain distinct version/source/role, lifecycle and
  idempotence checks. Removed a new redundant assertion of the constant closed
  preflight; the actual offline build receipt demonstrates zero provider calls.
  Corrected a map negative control so source tampering and false geometry receipt
  fail independently. No broad test-pruning or new model evaluation campaign.
- **Completed — final visual checks:** StLouis view and Tab/Enter district1
  selection worked in the actual browser. At a 320×700 viewport, document width
  measured305px, both map panels279.4px and stacked with identical bounds; no
  horizontal overflow. Restored desktop viewport, selected KC/district5 and saved
  screenshots outside Git. Inspected browser console had no errors/warnings.
  These are visual/keyboard checks, not screen-reader, bilingual or Pi proof.
- **Completed — independent findings/fixes:** reviewer reproduced acceptance of
  invented overlapping paths with a self-authored map receipt. Added an independent
  application-owned derivative hash/byte pin checked by server and browser;
  copied source metadata/true flags cannot authorize another map. Replaced the
  synthetic positive receipt test with the forged-receipt regression and labeled
  shape checks separately from actual GIS coverage proof. Reviewer also found that
  Stop could discard a late successful session ID. Matching submission identity
  now retains that ID in stop_requested for cancellation/reconciliation, never
  resumes or redispatches, and rejects conflicting IDs. These future remote
  lifecycle semantics do not claim a live cancellation guarantee.
- **Completed — verification:** required offline JS/Python/loopback gates and
  syntax/diff checks pass. Independent reviewer verified only the repaired cases:
  actual pinned derivative accepted, invented derivative rejected, stopped job
  retains late ID without resuming. No additional provider/GIS calls or blanket
  suite repetition in that follow-up. Human map/legal/rights and remote-cancel
  approval remain unproven.
- **Completed — commits/recovery evidence:** `bfd3fbf` records the official-map
  review and its independent derivative pin. Re-running the actual offline
  candidate compiler at03:46:13 UTC produced the same bundle hash
  `26ff2a77361d873d6494c987461209ad732c2f5e02a3896f0e9faa38f010702b`,
  reused the durable logical job identity and remained cancelled_locally, without
  session creation or additional spend. Opened that local bundle for review.
- **Completed — final browser admission:** after restarting only the owned map
  server, the application-pinned derivative loaded in the actual browser and KC/
  district5 highlighting worked. Final screenshot retained outside Git. Providers
  remain disabled on this map-review server.
- **Planned:** publish focused map/evidence commits to existing draft PR6 and
  verify its actual remote CI. Keep managed inference, publication, bilingual
  civic release, human voice and Pi gates held; no new approval is assumed.
- **Completed — published/CI:** pushed focused commits `bfd3fbf` (maps) and
  `518faf2` (offline evidence/closed paid gate) to draft PR6, and updated its
  description around actual artifacts, evidence and limitations. GitHub Actions
  [run40059695820](https://github.com/daniel-p-green/open-oracle/actions/runs/40059695820)
  for518faf2 completed successfully. CI uses no credentials/providers; GIS and
  visual verification remain separately recorded local evidence. Working tree
  was clean after the push. No merge, deployment or new API usage occurred.

## 2026-10-24 UTC — Library delivery and budget clarification

- **Completed:** parent explicitly requested saving the finished map screenshot
  to Library. Read the actual Library skill and current transfer helper; saved
  `map-review-kc-final.png`, received a confirmed Library file identity and
  verified its local identity metadata. Private receipt retains the ID for
  main-chat delivery. Image SHA256 begins `74cb8537bc98fc5f`. No public sharing,
  source-archive upload, inference or new credential occurred.
- **Completed — clarified server controls:** rechecked Agents configuration,
  create schema, errors, cancellation/recovery, model limits, pricing and Platform
  spend limits. Important nuance: `session_budget_exceeded` documents an internal
  server budget; no caller-set amount/units or $5 procedure was found. Platform
  hard limits exist but can overshoot during propagation; no billing setting was
  changed or actual current enforced limit re-inspected. Earlier per-session-cap
  wording must not be read as claiming that no server budget controls exist.
- **Completed — concrete financial analysis:** no-tools/no-sandbox/subagents-off
  removes those cost sources, but the inspected contract does not bound managed
  model work. The quickstart's Astra has 128k maximum output; at current Standard
  $50/M that is $6.40 before input. A lower managed internal ceiling may exist
  but was not verified; this is model-limit arithmetic, not a measured job bill.
  A conditional 2k input/1k total-output scenario
  is about $0.07 per invocation, not a measured managed job quote or $5 ceiling.
- **Proposed, not run:** one-shot Luna Responses extraction, exact input count
  capped at 8,192, server `max_output_tokens:1024`, no tools/history/background,
  default tier, standard mode/effort none, no retry, and $0.01 reserved. Published
  ordinary token estimate $0.0013312; conservative higher-input-rate estimate
  $0.00256. This is a bounded alternative to the managed harness, not an Agents
  recovery evaluation. Parent decision needed on the harness substitution or a
  deliberate relaxation of the earlier managed hard-stop condition. Current
  instruction forbids paid inference, so neither was executed.
- **Completed:** wrote [exact controls, exposure and supported next step](docs/rebuild/AGENTS-BUDGET-REVIEW.md).
  No new tests, SOS retries, deployment, microphone or speakers. Prior shared
  reservations and usage estimates remain unchanged.

## 2026-10-24 UTC — product completion correction and integrated milestone

- **Direction:** Daniel correctly rejected interpreting the harness/map checkpoint
  as a completed multilingual voice/generative-UI product, and set developer-
  profile/public-demonstration quality as the completion bar. Continued work
  remains bounded by consent, privacy, primary sources, existing API budget and
  publication restrictions. Managed Agents is deferred; bounded Responses is
  acceptable for implementation but not an Agents comparison.
- **Running:** integrated web entrypoint replacing separate reviewer-facing
  surfaces, with diagnostics preserved. Added a concrete user-workflow acceptance
  matrix, explicitly not complete/public-ready. Prioritize source-backed typed
  views, map integration, English/Spanish interaction, speech/currentness and
  coherent error/reset behavior. No new microphone/speaker authority inferred.

## 2026-10-24 UTC — integrated workspace and checked prepared voice

- **Completed, local review:** one web entrypoint now composes scope, explanations,
  exact originals, coverage gaps and synchronized official maps from typed
  components. Prior fixture/provider harness remains at `/diagnostics`.
  English/Spanish interface and map controls share question/language/reset state.
  Spanish civic answers remain held; navigation translation is not legal review.
- **Completed, metered:** one real `gpt-6-luna` Responses UI composition returned
  admitted map component IDs inside the browser journey: 126 input / 24 output
  tokens, approximately $0.0000246 at verified Standard pricing. No raw visitor
  question, factual prose or arbitrary UI markup went to/from the planner.
  Server-side enablement, one/two-run limit, owner token, idempotence and ledger
  reservations remain explicit; provider-off composition remains available.
- **Completed, synthetic only:** prepared three `gpt-live-1` clips: English rate,
  English map navigation and Spanish map navigation. Full transcript equality,
  final close/usage, no backend events and nonempty bounded PCM passed before
  retaining local WAV fixtures. These intentionally retained generated examples
  are not human recordings. Bytes stay outside Git, pinned by application-owned
  metadata. No microphone or speakers were activated. English/Spanish navigation
  audio is not a complete multilingual voice agent or acoustic validation.
- **Cost evidence:** Live final usages 20 + 19 + 19 seconds, approximately
  $0.0483333. New composition plus audio estimate $0.0483579. Shared conservative
  reservations $0.71; aggregate direct usage-price estimate $0.0727494, excluding
  earlier unmetered Playground usage. Estimates are not invoices. No recharge,
  purchase, billing change, credentials or managed Agents run.
- **Independent review and repairs:** scoped keyword canonicalization could
  answer an unrelated tax/measure with COMBAT facts; replaced with finite aliases
  and abstention on mismatched/mixed questions. Gated examples during source
  initialization, preserved core explanations on optional service failure,
  repaired Stop cancellation/request correlation, bounded start/body/poll waits
  and audio fetching, and fenced late playback promises. Focused owner-boundary
  checks cover these risks without a test-count target. Whole offline suites
  passed before the last source addition; final verification follows below.
- **Completed, primary-source clarification:** independently downloaded distinct
  official KCEB public sample `01-00006-01-NON.pdf` (not a retry/bypass of denied
  SOS originals). SHA256 `d33d41b4c377e7d9d1bd63af0c2f1053bc4b63f608eb3167200a8385e576e0fc`,
  retrieved 2026-10-24T04:32:39Z. Rendered/visually checked page 2 under the actual
  installed PDF skill. The referendum is labeled Proposition A. Added its exact
  question and page/version attribution beside the map comparison, with the stay
  caveat; no personal ballot inclusion inferred. Original PDF remains private
  outside Git. Map reuse/public release gates remain unresolved.
- **Running — requested Claude gate:** installed CLI supports Opus 5.5 High, but
  its separate subscription's extra-usage status was unverified. Used the existing
  signed-in Chrome Claude account instead: UI explicitly showed Opus 5.5 High,
  included capacity, usage-credit balance $0, monthly cap $0 and auto-reload off.
  No billing/access changes. Sent only a scrubbed 18-file OpenOracle source and
  relevant instruction bundle, excluding credential identifiers/private inputs
  and unrelated material. Requested no memory/connectors/tools. Critique pending;
  no acceptance or review-completion claim until its returned result is read.

## 2026-10-24 UTC — Opus critique dispositions and substantive review repairs

- **Completed — actual requested review:** existing browser visibly selected
  Opus 5.5 High and returned a detailed **not ready** critique. The reviewer cannot
  introspect client effort; High was independently observed in the UI. Preserved
  the actual result privately and documented findings/dispositions in
  `docs/rebuild/CLAUDE-REVIEW-2026-10-24.md`. A focused re-review is running, not
  yet accepted or counted as complete. No unrelated material/credentials sent.
- **Completed:** verified content now renders immediately; optional AI action
  truthfully chooses card order from fixed options. Unsupported/one-order topics
  and language switches do not automatically spend runs. Added local confirmed
  topic choices instead of silently misrouting paraphrases. Fixed separate advice,
  membership and unsupported statuses. Review-only tools/old routes/unheard audio
  require an explicit local flag. Default surface withholds unreviewed clips.
  Fixed replay, generic navigation re-preparation, owner refresh exhaustion,
  browser cross-site capability access, source page citations and idle warning/
  scroll activity/focus behavior. New code formatted with pinned Prettier 3.6.2;
  no project dependency added. Restricted/offline formatter lookups failed; the
  authorized pinned registry invocation succeeded. No test-count goal.
- **Completed — legal provenance:** downloaded official Court opinion
  `26a388_q86b.pdf`, SHA256
  `73ef64de152e4dc257baa83767b75eb19fe6aea473be8688b61644c0741afd2e`,
  retrieved 04:35:42Z, rendered/visually checked page 2. Retained official docket
  HTML SHA256 `e184ad387a37923ade5883b05c13df2a61aaf09183f165f6827b9be2b8c99139`,
  retrieved 04:36:15Z; its latest listed proceeding is September25. Legal statement
  is now a separately pinned as-of record with a 24h review deadline. Missing,
  changed or expired record withholds the assertion; neutral map labels remain.
  This does not settle every challenge or grant publication/rights clearance.
- **Completed — audio measurement/correction:** review's padding inference was
  confirmed by 20ms RMS windows. Preserved original generated WAVs, trimmed
  leading/trailing silence with 200ms margins, repinned derivatives: 6.68s, 8.60s,
  11.46s. Re-transcribed actual trimmed public synthetic files with account-
  verified `gpt-transcribe`; all three match expected text after punctuation
  normalization. No human capture/playback or human pronunciation approval.
  Three calls reserve $0.03 and estimate $0.0020055 using measured supplied WAV
  duration and current price; this is not returned provider-meter/invoice usage.
  Shared reservations $0.74; combined usage/duration price estimate $0.0747549,
  excluding earlier unmetered Playground charges. No new credits/access/billing.
- **Completed — actual UI checks:** integrated desktop and 390px-viewport Spanish
  maps/controls/current transcript/silent re-exercise inspected. Observed page
  width and scroll width both375px (browser scrollbar), no horizontal overflow.
  Actual device/screen-reader, nonauthor comprehension and human acoustic checks
  remain unverified. Screenshots retained privately outside Git.
- **Not adopted:** Claude suggested using a Live utterance-complete event;
  verified official docs explicitly lack that boundary. Kept full-session close
  gate and documented bounded pre-generation latency. Do not treat a pause as
  permission to release partial speech.
- **Consequential next decision:** raw cloud microphone capture cannot guarantee
  the standing no-DOB/address/private-voter-data rule. Proposed local speech
  transcription before public admitted categories cross the cloud boundary is a
  stack deviation requiring project-lead direction. No speech-model download,
  new credentials, microphone/speaker activation, public release or Pi changes.
  Continue source-backed product work; prepared narration/card ordering is not
  the full multilingual voice/generative-UI concept. Acceptance matrix updated.

## 2026-10-24 UTC — final integration proof before commit

- **Completed:** focused Opus re-review returned, confirmed most repairs and
  withdrew the unsupported Live completion-event suggestion. Its two medium
  findings (unknown versus coverage-gap copy, premature/stale ordering control)
  were repaired and demonstrated. Final short closure request remains running.
- **Completed:** independent reviewer reproduced token-expiry orphaning with a
  gated dummy job, then verified the repair. Expired owners cancel and retain
  draining workers, block concurrent dispatch, reject stale tokens and disappear
  after cleanup. Ordering requires a complete current component set and cannot
  claim success without application. Targeted ownership proof passed.
- **Completed — final real path:** on a fresh explicitly enabled single-run
  server, both maps/exact question were visible under local composition before
  the optional ordering click. One real Luna request returned 126 input/24 output
  tokens, approximately $0.0000246; both maps remained and matching narration
  re-prepared. Allowance-used state prevented another run. A raw paraphrase then
  showed unsupported/confirmation controls and reached the rate with one click,
  without transmitting that text. Play stayed disabled throughout.
- **Current costs:** all-worker conservative reservations $0.75; aggregate
  usage/duration price estimate $0.0747795, excluding earlier unmetered Playground
  usage. No invoice claim, purchase, new access or human audio activity.
- **Completed:** fresh default page hides unheard audio consent/review links;
  explicit review page prepares pinned clips but requires separate speaker
  consent. Current Chromium feature gate, malformed-date withholding, source-
  derived labels, UTC date, partial-Stop recovery and playback-error handling
  landed. Full offline/loopback checks and syntax/whitespace verification are
  run before the associated commit. Remote CI is checked after push, never
  assumed from local results. No public deployment or Pi modification.

## 2026-10-24 UTC — committed integration, CI and final review closure

- **Completed:** implementation commit `efd774e3a67e0628b4acf6a5db7d50b62680c8ee`
  pushed to existing rebuild branch and draft PR6. Actual credential-free
  [CI run40064264659](https://github.com/daniel-p-green/open-oracle/actions/runs/40064264659)
  completed **success**. Updated PR purpose, actual tests/costs and limitations;
  no merge/deployment. Working tree was clean after the implementation commit.
- **Completed:** final short Opus response closed both medium blockers based on
  supplied logic/browser proof, explicitly not a new source-delta inspection.
  Independent reviewer did inspect the repaired source and passed the precise
  ownership regression. Whole-product verdict remains **not ready**.
- **Follow-on correction:** adopted final feedback to make confirmation buttons
  explicitly name COMBAT/Missouri, preventing a California/property-tax question
  from confirming an unqualified tax topic. Existing workflow proof now covers
  both language menus. Added expiry invalidation for an already-visible legal
  note as well as initial source admission. Feature gate checks actual APIs,
  not browser identity. No new paid request or human audio activity.
- **Pending product-lead decision:** private spoken-input architecture deviation;
  candidate source/quote/rights admission and civic-language/acoustic/real-device
  validation remain pending, not denied. The earlier two SOS-original downloads
  remain blocked by HTTP403 and were not retried. Other useful authorized source
  and UI work is preserved; this checkpoint is not offered as full acceptance.

## 2026-10-24 UTC — latest code verification and review artifact

- **Completed:** focused follow-on commit
  `caf9c429f448ac5cdd3f06a15b10aadd1a94d897` pushed. Actual credential-free
  [run40064514490](https://github.com/daniel-p-green/open-oracle/actions/runs/40064514490)
  completed **success** for that code. PR6 records verified CI rather than a
  pending/local-only claim. Final documentation update does not change code.
- **Completed:** preserved actual returned critique/visible closure privately;
  final local review workspace is `http://127.0.0.1:8899/` with providers off,
  no active microphone and Play disabled absent deliberate speaker consent.
  Default surface was separately verified on8900; final single-use provider
  check on8901 is exhausted. Desktop/source-map screenshot is retained outside
  Git. Review browser tabs are kept for inspection, not presented as acceptance.
- **Still pending:** full multilingual spoken-input agent, broad source-backed
  generative evidence composition, candidate/source admission and human civic/
  acoustic/accessibility acceptance. No proof or approval is invented for them.
  Shared cost figures remain $0.75 reserved / $0.0747795 estimated plus prior
  unmetered Playground charges. No further paid calls, deployment or Pi work.

## 2026-10-24 UTC — original PRD/JTBD recovery and scope reconciliation

- **Completed — artifact delivery:** uploaded the existing integrated desktop
  JPEG to Daniel's Library using the installed Library skill/current transfer
  helpers; create and required xattrs succeeded, verified image size325287bytes.
  Private receipt and exact Library identifier are retained outside Git and
  returned to parent. This is a private review artifact, not publication or
  evidence of full readiness. No human sound or paid inference was activated.
- **User direction:** Daniel asked for the original PRD and jobs-to-be-done in
  the Hack Midwest directory. Parent directed pause on new product assumptions,
  exact inventory/version review and traceability before more architecture.
- **Discovery correction:** earlier rebuild reviewed history/implementation but
  had not established review of the original PRD/JTBD set. Configured
  HackMidwest2026 project root is `/Users/danielgreen/Documents/Codex`. Located
  and read October9 PRD/context, October10 stretch PRD including section4 JTBD,
  and October12 OpenAI-only Pi planning/decision/reconciliation/acceptance/
  checkpoint/README/TODO documents. Dated SHA snapshots and exact read scopes
  are in `docs/rebuild/ORIGINAL-PLANNING-INVENTORY.json`; duplicate stretch PRD
  is byte-identical and original is untracked, not a separate approved revision.
  Targeted search is not exhaustive review of all Mac/cloud planning documents.
- **Consequential recovered requirements:** final scope includes both election
  authorities and all Jackson County ballot variants/candidates/measures;
  distinguish inventory/applicability/evidence/experience coverage. Original
  resident jobs include office orientation, simpler wording, fresh follow-up,
  source challenge/correction, optional teach-back and recap. Current finite
  harness does not satisfy them. Statewide ambition and numerical study gates
  remain draft proposals, not current authorization or measured results.
- **Recovered recorded decisions:** October12 02:50:58UTC selects GPT-Live
  adaptive generated conversation and rejects substantive prerecorded routing
  as release/fallback;02:52:23 allows startup/loading greetings only. COMBAT is
  excluded from showcase/demo/pilot in those records; current authorized
  COMBAT provider tests are engineering reference, not an explicit showcase
  reversal. Amendment7 was only a candidate. Keep latest official-map direction.
  Earlier campaign-marketing exclusion versus later attributed-statement
  permission needs reconciliation; current campaign excerpt stays held.
- **Reuse:** found clean later Mac-first OpenAI-only repo at
  `2026-10-11/task-16/open-oracle-pi`, HEAD`cc0bf50`. Its checkpoint reports
  synthetic/build/browser evidence, explicitly no live/human/acoustic readiness.
  Targeted source inspection confirms expressed preferences, scoped bindings,
  session Stop/Erase and hash/span/expiry admission concepts. Complete audio/
  sideband audit and real-provider validation have not been repeated. Preserve
  original work and inspect owners before importing; no silent wholesale port.
- **Completed:** concise requirement-to-implementation/gap mapping, retain/
  replace/reconsider decisions and corrected next milestone documented in
  `ORIGINAL-PLANNING-RECONCILIATION.md`; roadmap/index/initial-decision pointers
  and current AGENTS precedence updated. AWS/time-bound event/$100 instructions
  are historical; latest $200 authorization and media/publication gates apply.
- **Validation:** documentation/source-snapshot work only; compare exact hashes,
  inspect links/staged diff and run whitespace checks. No extra tests for count,
  no whole-product acceptance claim. Existing local test-audit skill consulted;
  proportionate verification retained. No new paid requests, SOS retry, install,
  credential change, deployment or Pi modifications.
- **Next:** assess recovered owners for reuse against current API/privacy
  contracts, then implement the connected public-source typed/synthetic journey.
  Complete renewed Opus5.5High substantive-delta review before readiness claim.

## 2026-10-24 UTC — restore the resident journey; stretch level authorized

- **User authorization/scope:** Daniel explicitly authorized implementing the
  recovered stretch level using development best practices. D2 now governs the
  acceptance target with later official-source/OpenAI/multilingual/generative-UI
  changes. Preserve statewide ambition and complete Jackson County/KCEB/JCEB
  proof. No new publication, credential, human-media or spending authority.
  Parent later relayed the official API showcase as inspiration; parent owns
  that broad read-only research, so this worker did not duplicate it.
- **Completed — reuse assessment:** read later Pi architecture, retrospective,
  OpenAI contracts and engineering review; inspected its contracts/session/
  playback/operator/evidence/pipeline/audio owners. Reused current createSession,
  Jobs/budget/cancellation and provider-job transport; no second session/media
  controller, whole older app migration or dependency installation. Exact
  scope/limits are in `docs/rebuild/REUSE-ASSESSMENT.md`.
- **Implemented:** official Proposition A/map journey with fresh overview,
  simpler wording, more detail and limits; exact original/source disclosure;
  local clearly labeled Yes/No effects with no model call; optional No-vote
  teach-back, disputed-unit withdrawal and ephemeral language-filtered recap.
  New default examples/fallback omit COMBAT. Candidate action remains an honest
  coverage gap, not an invented/partial complete roster. Campaign excerpt held.
- **Implemented — actual adaptation/privacy:** requests contain only selected
  public operation/language and optional parent request ID. Backend retrieves
  its own ready same-owner public unit, rechecks source version and supplies it
  as context; no raw visitor text or client-supplied history. Erase revokes
  server references. Ready public units retain at most owner10minute lifetime,
  pending work retains120s expiry. Confirmed unstarted409 restores local
  allowance and clears stale parent, with deliberate fresh action only.
- **Implemented — release/operation bounds:** pinned original, exact effects,
  source IDs, number-word/time/congressional-scope gates and free-prose vote
  outcome guard. Generation then separate Decisions review, no constant-input
  routing call. Original wording loads before optional geometry. Source/map/
  recap/teach-back browsing use a separate region and do not cancel text;
  Stop/Erase/language changes still invalidate. Spanish civic generation and
  teach-back remain held outside review mode; server preflight precedes spend.
  Default1, maximum8 explicit process runs permit a bounded connected journey;
  shared ledger cap200 remains authoritative. No automatic paid retries.
- **Actual independent review:** requested Opus5.5High was again visibly selected
  in the existing authorized Claude UI. Scrubbed relevant source/requirements
  uploaded; actual critique and source re-review returned. Found effects
  inversion, cross-slot prose risk, stale source views, Spanish bypass, geometry
  coupling, misleading labels/caps and missing actual adaptation. Repaired.
  Re-review accepted earlier findings, then found120s-parent expiry and disputed
  parent reuse; those were repaired with focused ownership/client proofs. Exact
  effect reversal under a false-positive fake reviewer is rejected. Indirect
  semantic inversion still depends on fallible model checks, not a guarantee.
- **Actual browser evidence:** original/source, local recap and language controls
  exercised. Provider-off instance without geometry retained readable original
  and precise missing-map state. Default Spanish teach-back/generation disabled;
  reset removed journey state. During a real generation, opening its original
  and moving the map preserved pending text and the source. No human microphone,
  speaker, playback consent or Play action used. Existing idle clear removed
  prior review content; no screenshot falsely reconstructs a cleared result.
- **Actual API results — not acceptance:** initial English generation reached
  display/recap; Spanish simpler output held. Stricter subsequent English
  attempts held. A scripted diagnostic retained only public generated text and
  scores privately, showing support0.87/polarity1.0. After stronger attribution,
  same-source Luna/SolLow comparison held at0.85/0.91 support (polarity1.0).
  Opus found small real Luna drift and no clear material Sol defect; that is its
  opinion, not proof or a model-winner claim. Both account model calls completed;
  no access grant/credential change. Official Sol docs reject None effort;
  code uses Low/1536total output tokens and$0.10 reservation, versus Luna512/
  $0.01. Both requests bounded12,000serialized bytes, no tools/background/retry.
- **Quality evidence:** one four-control Decisions request accepted an
  engineering-labeled faithful control and rejected inverted/unattributed/
  personal claims. Following Opus advice, split review into cited-evidence-only
  entailment, no additions, attribution, request fit and polarity, keeping0.95.
  Two bounded calls evaluated six distinct engineering-labeled variants: all
  four adverse variants held, both intended faithful variants also held on
  request-fit0.94 or attribution0.94. Time drift passed the model but code held
  it. This small development set is not independent calibration or accuracy.
- **Current cost evidence:** conservative shared reservations$0.94;
  usage/duration price estimate$0.0788082 recorded in the private shared ledger, excluding
  prior unmetered Playground charges; not an invoice. Sol cache-write pricing
  uses a conservative12h allowance if such tokens appear. No credit purchase,
  billing change, managed Agents inference or private speech transmission.
- **Independent primary evidence work:** retained the public U.S.House office
  explanation original at2026-10-24T05:58:07.441959Z, SHA256
  `2db1232424310e0844870902e01c976dcc52bf613d04798beb28203d345b7cdf`.
  House terms distinguish government-produced material from transferred
  copyrights; no images or broad license claimed. Extraction/admission remains
  pending; no ZIP/address representative lookup. No denied SOS retry.
- **Verification:** focused false-positive/polarity/source, server-owned context/
  expiry/revocation and confirmed-unstarted client proofs pass. Existing Node
  suite and Python suite passed before latest small expiry/review changes;
  required suites/syntax/whitespace run again before commit, remote CI checked
  after push. No test quota, acoustic validation or whole-product claim.
- **Still running work:** semantic review interface needs to separate factual
  eligibility, explicit application source attribution and requested delivery
  quality without lowering factual gates to force a demo. Fresh checked voice,
  natural input, candidate/office coverage, bilingual/human accessibility and
  resident comprehension/operational evidence remain open stretch requirements.
- **Reference research received from parent:** adopt Tempo's separation of
  bounded workflow actions from grounded Responses, uncertainty/quotas and
  server-only credentials; Lumen's evidence-bearing viewport/accessibility
  checks and Loupe's distinction between applied and visually verified fixes.
  Solar System's MIT WebRTC/visual pattern is a reference only; no source has
  been imported and no Realtime-for-Live substitution made. Chatkit map/chat
  concept does not justify small-screen exclusion or unlicensed code copying.
  Tempo/Lumen/Loupe root-app licensing remains unestablished; no wholesale ZIP
  source reuse. These concepts reinforce current owners/contracts, not new
  infrastructure or election/Spanish-quality proof.
- **Completed before commit:** required Node/provider-off Python/loopback suites,
  updated-module syntax and whitespace checks passed after the final repairs.
  Remote CI is checked after pushing; no success is inferred from local output.

### 2026-10-24 06:49 UTC — resident adaptation, source role and review workflow

- **Completed:** `5ebe3c1b13ec0ac9f6dc4b4e564fa1bd75891756` pushed to draft
  [PR6](https://github.com/daniel-p-green/open-oracle/pull/6); actual remote
  [CI success](https://github.com/daniel-p-green/open-oracle/actions/runs/40068954427).
- **Actual Opus5.5 High proposal critique:** visibly selected in the authorized
  Claude UI, returned four concrete conditions: sentence-level source
  attribution, paraphrase versus quotation labeling, critical request fit for
  limits, and visible simplicity/detail uncertainty through recap. Implemented;
  factual predicates retain0.95. Attribution is enforced sentence by sentence
  by application rules; attribution/simpler-detail quality scores are advisory.
  No score is a factual or bilingual certificate. Renewed substantive review
  remains required before acceptance.
- **Actual bounded quality result:** six engineering-labeled variants evaluated
  with the revised source-role interface: two faithful variants eligible,
  four adverse variants held. Time/scope/unattributed prose held deterministically;
  indirect semantic inversion still depends on fallible model review. This
  small development set is not calibration, statistical accuracy or a guarantee.
- **Actual provider/browser result:** SolLow English overview → simpler English
  follow-up → Spanish adaptation all completed, using actual server-owned prior
  checked public units. Original, recap, language and map controls exercised;
  no microphone, Play, speaker consent or heard audio. Private proof screenshot
  `openoracle-fresh-resident-journey.png` predates subsequent visual polish.
  Shared reservations now$1.26, direct usage/duration estimate$0.0863188, excluding
  earlier unmetered Playground charges; not an invoice. Latest three estimated
  costs$0.0020121/$0.002193/$0.0024544. No automatic paid retries.
- **Implemented/observed:** official House office passages admitted from the
  retained official original and limited government-material terms. Byte and
  passage hashes checked; no images, leader names, addresses, district matching,
  candidate roster or blanket reuse license. Source/UTC retrieval/original
  English label visible; Spanish civic translation remains pending.
- **Implemented/verified:** preserved same-language action nodes; late answer
  no longer moves focus or replaces optional activity. A clearly labeled
  delayed mock browser run (zero API calls) preserved teach-back and focus;
  independent source re-review closed the exhausted-ordering cleanup-token bug.
  Token remains for Erase/cancel even after inference allowance reaches zero.
- **Visual evidence:** actual desktop two-column source/maps inspected; narrow
 390px effects and Spanish original-office states had390px document width.
  Map originals/versions are progressive disclosures, original PDF links remain
  direct, Stop remains available, legal links separated. These are rendered
  viewport observations, not phone, screen-reader, acoustic or WCAG acceptance.
- **User direction / references:** Daniel requested why/how notes. See
  [the reference/adaptation record](docs/rebuild/DEMO-REFERENCES.md) for exact
  URLs, considered versus applied patterns, files, evidence and licensing limits.
  No demo source code imported, upstream commit fabricated or axe scan claimed.
- **Actual skills:** consulted installed `oracle` (`@steipete/oracle`) review
  guidance; Daniel's explicit Claude selection overrides its default reviewer.
  No separately named Peter testing/software-engineering skill found in the
  targeted catalogs/search. Existing test-audit guidance is OpenClaw-adapted,
  not attributed to Peter. Ballot-accessibility-audit guides source/readability
  barriers; no readability score or automated accessibility proof invented.
- **Verification:** Node behavior suite passed; Python source/jobs/loopback
  suite passed after loopback sandbox escalation (default bind was denied,
  authorized escalation succeeded). No paid calls in these suites. Syntax and
  whitespace checked before commit. No tests added solely for count.
- **Running:** fresh per-answer checked speech, meaningful typed visual
  composition, candidate/variant coverage and actual human bilingual/accessibility
  validation remain open. This milestone does not meet full stretch acceptance.

### 2026-10-24 07:06 UTC — fresh speech integration; external verification blocked

- **Completed locally:** resident/source-role/reference increment committed as
  `f0c3ef8` (not pushed). [Demo reference notes](docs/rebuild/DEMO-REFERENCES.md)
  explain actual adaptations, considered ideas, versions not established,
  affected files, licensing and verification limits.
- **Implemented:** fresh per-answer speech job derives all prose from its
  ready same-owner checked public parent. Reuses ProductPipeline, Jobs, Budget,
  session and SpeechOutput; no second controller or substantive recording
  library. Spoken reading preserves sentence attribution, paraphrase label,
  unconfirmed delivery, pending human review and nonpersonal scope.
- **Implemented:** complete GPT-Live session buffering/finalization, exact
  co-transcript check, then independent whole-WAV `gpt-transcribe` without
  expected text or language hints. Detected language and lexical comparison
  preserve numbers/negation; mismatches hold. No unsupported per-answer done
  event, transcript-only release or guessed pause-as-completion claim.
- **Bounds:** each speech task reserves$0.10 for one Live session and one ASR
  request, no retry. Canonical reading≤1000characters; Live generation52s,
  transport timeout82s, accepted final usage≤75s; PCM≤60s, ASR HTTP20s. Accepted
  duration arithmetic$0.067, not invoice, refund promise or vendor hard cap.
  Uncertain costs retain the full reservation. Long buffering remains a known
  release-latency defect; no natural-conversation performance claimed.
- **Implemented/verified locally:** owner-authenticated memory-only WAV access,
  parent cancellation/expiry cascade, ready-result revocation, browser lease
  expiry, server revalidation before manual Play and post-await expiry check.
  Source/office/teach-back/recap/map actions stop cached and pending speech while
  preserving independent pending text. No keys/capabilities in URLs or browser.
  Existing no-store/CSP/microphone restrictions preserved.
- **Actual independent code review:** found server/browser EN-unconfirmed
  reading-space mismatch and expiry-during-Play-revalidation race. Fixed; exact
  cross-runtime EN/ES confirmed/unconfirmed parity and fake-player zero-creation
  expiry probe passed. Later reading-action review found map navigation only
  stopped cached speech; changed it to the existing pending-speech invalidation
  path. No new agents, paid checks or test-count target.
- **Actual zero-API browser proof:** visibly labeled mock completed fresh answer
  → preparation → displayed full canonical reading, consent unchecked and Play
  disabled. Challenge cleared audio/transcript and restored original. This is
  mock integration evidence, not live waveform/acoustic validation. Found that
  an empty old-clip library hid speaker consent; fresh preparation now reveals
  that control without checking it or activating sound.
- **Current official docs checked:** `speech-to-text` transcriptions guide and
  `/v1/audio/transcriptions` spec; Live conversations/session close; data controls.
  Added visible per-service data disclosure: Responses/Decisions/Live abuse logs
  may retain content up to30days with exceptions; transcriptions table lists
  no content state/abuse retention. Responses/Live explicit store:false, no
  verified account ZDR claim; local Erase cannot unsend provider data.
- **Completed Library delivery:** real earlier public-source ES adaptation/maps
  image saved as `libfile_66e195abb528819198c8b40286f4ad19`, version0,
  `openoracle-fresh-resident-journey.png`. Upload and local identity persistence
  confirmed. It predates latest visual polish and proves no heard speech.
- **Denied — Git push:** automatic approval review rejected pushing `f0c3ef8`
  to existing draft PR6, citing initial repository-publication prohibition and
  treating later delegated PR authorization as untrusted. Command did not
  execute. No alternate route or retry; explicit approval question pending.
  Therefore no remote CI result exists for this local commit.
- **Denied — renewed Claude review:** automatic approval review rejected upload
  of the scrubbed eleven-file source/review bundle to existing Opus5.5High chat,
  citing absent external-message/payload authorization. Existing model setting
  visibly verified. Read-only outcome check found no new attachment; dismissed
  upload dialog. No retry/alternate route; explicit approval question pending.
  Prior returned critiques remain actual evidence, not a new speech review.
- **Denied — real OpenAI smoke:** automatic approval review rejected starting
  loopback8912 with existing secure access for two runs/$0.20 reservations within
  shared$200, citing absent paid API approval. Process did not start; no calls or
  new charges. No old enabled server/alternate route used. Explicit specific
  approval question pending. Ledger remains reservations$1.26 and recorded
  estimate$0.0863188 plus prior unmetered Playground usage, not an invoice.
- **Verification:** Node behavior suite, Python provider/source/jobs/loopback
  suite, targeted client expiry/revocation and cross-runtime reading checks
  passed after repaired private-method signature regression. Full required
  checks run again only for the latest substantive UI repairs before commit;
  remote CI cannot validate an unpushed commit.
- **Still open:** actual new provider speech/latency, renewed Opus critique,
  natural private-safe input, richer typed generative composition, complete
  candidate/variant evidence, map access/rights and human bilingual/acoustic/
  screen-reader/comprehension acceptance. No public-readiness claim.
- **Final browser repair evidence:** delayed zero-API speech was cancelled by
  selecting the St.Louis map view. After the delayed fake finished, voice stayed
  off, transcript stayed cleared, consent remained false and Play disabled.
  Reset removed the journey. This directly verifies the repaired sibling path;
  no real waveform or device was involved.

### 2026-10-24 07:51 UTC — approvals reconciled; actual speech evidence and repairs

- **Authorization reconciled:** parent supplied the original verbatim Daniel
  directions for project commits/PRs, relevant Claude source review and OpenAI
  testing within the shared$200 cap. Each previously denied action was retried
  once on that new evidence, and all three were permitted. No alternate route
  bypassed a denial. Earlier approval questions are superseded by this supplied
  authority; no request identifier was exposed by those question tools.
- **Completed:** pushed `f0c3ef8` and `dd6c1ac9cdde67179aeee87dd72d4543461aa9a1`
  to existing draft PR6. Actual [remote CI success](https://github.com/daniel-p-green/open-oracle/actions/runs/40073255602)
  fordd6c1ac. No merge/deployment. Later uncommitted repairs need their own CI.
- **Actual requested review:** current scrubbed eleven-file source bundle
  submitted to the existing Claude chat, UI visibly Opus5.5High. Actual critique
  and focused patch re-review returned; full product remains not ready. Found
  expected silence padding, lease pressure, wasteful source-navigation cancel,
  overlong paid readings and typography false holds. Dispositions below follow
  source review and measurements, not presumed reviewer correctness.
- **Implemented/checked:** speech ready lease120s from ready, hard240s from
  request/owner cap; before and after async server validation, Play needs clip
  duration+2s remaining. Ready touches existing session. Same-parent source/map/
  activity browsing now halts active playback while retaining pending/cached
  preparation; explicit Stop/Erase/Challenge/language/parent change still revoke.
  This supersedes the earlier cancel-on-map behavior recorded above.
- **Implemented/checked:** before reservation, a conservative12characters/sec
  heuristic rejects readings estimated over45s; a known no-start restores local
  allowance without retry. Closed pronunciation aliases cover dotted AI/IA,
  only House Bill No1/numberone, and2025 spoken forms. Standalone no/negation,
  other numbers and qualifications are not silently removed. Primary detected
  ASR language must match. Live transport90s/client115s; source/numeric/factual
  thresholds unchanged.
- **Actual initial smoke:** Sol/Decisions overview ready ($0.10 reserved,
  $0.0019515 usage estimate). Stopped old server before speech to apply review
  fixes. Remaining$0.10 tested the adapter against the exact observed public
  checked text, explicitly not restored ownership/full web proof. Live omitted
  the final personal-ballot limitation; held before ASR, no audio released.
  Final Live usage52s, PCM51.52s, leading/trailing low-energy0.66/27.84s,
  elapsed57.07s, window-bound close, estimated$0.0433333. Initial$0.20 allocation
  exhausted conservatively; no automatic retry.
- **Measured correction:** moved nonpersonal scope ahead of prose, keeping
  explanation/not-quotation label adjacent to prose and identical EN/ES server/
  browser reading builders. Fresh Live uses the officially documented
  instructions.append exact-disclosure request with content markers; startup
  waits for that instruction. Commentary remains only in the old diagnostic
  path. A complete canonical co-transcript plus1s low-energy interval proposes
  session close, never release. All final audio, including close-wait deltas,
  still receives whole-WAV independent ASR. No quiet-word trimming introduced.
- **Actual separately reserved development test:** $0.10, same public observed
  input. Opus reviewed the correction and found no consequential blocker for
  that bounded adapter experiment. Passed independent ASR with primary en,
  all disclosures present. Prepared in34.85s; PCM28.96s; leading/trailing
  low-energy1.06/1.08s; planned-text-and-quiet close. Pre-instruction PCM was
  silent by the measured threshold, no voiced output detected. Estimated
  $0.0263387. This is an English adapter pass, not human listening, Spanish
  meaning, reliability statistics or the full real web path. Latency remains
  unsuitable for the intended natural interaction.
- **Actual subsequent web check:** separate two-run$0.20 allocation; Sol text
  ready, source/map browsing stayed available during real speech preparation.
  Speech held at independent_transcript_mismatch. Live29s and WAV29.08s metered;
  estimated$0.0263477 for speech. Play remained disabled/consent false, focus
  remained on original source. Ordinary app deliberately kept no raw provider
  transcript. Instrumented public-only diagnostic is running under a separately
  capped two-run$0.20 allowance to identify actual mismatches; this private test
  wrapper is outside Git and never records human input. No automatic retries.
- **Cost checkpoint before that new diagnostic starts calls:** shared reserved
  $1.76; recorded aggregate estimate$0.1862414667 plus earlier unmetered
  Playground usage, not invoice. Existing credentials only; no account/billing,
  recharge, persistent access, public deployment or human media change.
- **Independent code review:** confirmed revised lease/preflight/canonicalizer/
  halt controls and focused local checks. Root also repaired ready-audio cleanup
  on Stop and tombstone saturation: known jobs remain cancellable at capacity;
  saturation blocks a delayed new Start instead of letting it evade Erase.
  Existing meaningful cancellation proofs extended; no test-count target.
- **Primary evidence increment:** used installed PDF skill/Poppler, visually
  checked page1 of the retained hash-verified KCEB public sample. All three
  U.S.House District5 rows plus write-in now visible, in ballot order, with
  equal background-evidence gaps. Source fixture has exact field spans, page,
  publisher, original/readout hashes and retrieval date. No person-record merge,
  policy inference, full-county inventory or personal membership claim. Actual
  provider-off browser verified all names/source. Missing/altered roster holds.
- **Useful HackMidwest work recovered:** read JCEB contest inventory and retained
  notice transcription: it reports48 printed contests outside KCMO, not an
  individual's ballot. Original PDF exists locally. It is a reuse candidate,
  not newly admitted/currentness-verified coverage; no complete denominator
  asserted. No denied SOS retry, campaign admission or bulk ingestion.
- **Official API freshness:** current text-to-speech guide says tts-1/tts-1-hd/
  gpt-4o-mini-tts shut down January6,2027; recommended migration is the different
  Realtime workflow. No deprecated TTS replacement silently introduced. A faster
  checked-speech comparison remains an architecture/evaluation follow-up.
- **Validation:** full local Node and Python/source/jobs/loopback suites passed,
  current EN/ES confirmed/unconfirmed reading parity passed. These are behavior
  proofs, not bilingual/acoustic/accessibility acceptance. No human sound used.

### 2026-10-24 08:11 UTC — terminal public web proof and checkpoint

- **Completed diagnostic:** real Sol/Decisions text → same-owner Live reading →
  independent whole-WAV ASR → authenticated browser fetch/hash/preparation
  reached ready. Instrumented test recorded26.82s PCM,33.02s preparation,
  planned-text-and-quiet close,1.20/1.10s leading/trailing low energy, primary en
  and complete canonical word agreement. No voiced output before instruction.
  Source/map browsing did not cancel it; original retained focus. No human mic,
  speaker consent or Play. After lease expiry the browser had cleared audio;
  a stale prepared-status string was observed and repaired with an explicit
  expired state/server cleanup. Focused expiry proof passes; this is no acoustic
  or full-acceptance claim.
- **Cost checkpoint:** shared conservative reservations$1.96; recorded aggregate
  usage/duration estimate$0.2127044667 plus earlier unmetered Playground usage,
  not invoice. Last text estimate$0.0019515; last speech$0.0245115. All provider
  jobs terminal; no automatic paid retries, purchases or billing changes.
- **JCEB reuse verified:** one permitted direct official download returned200 at
  documented URL,109533bytes, retrieved2026-10-24T07:57:44.986988Z, SHA256
  `032814e650dbdbdb0064acb396ead6f51dcd087778240802eb6c30c7a5ef64a2`.
  Byte-identical to retained October9 original, two pages. This substantiates
  reuse of HackMidwest source work; retained48-contest inventory is a candidate
  for admission after original-layout/field reconciliation. It is not a newly
  admitted personal or complete-county ballot. No SOS retry or bulk ingestion.
- **Local voice feasibility check, not implementation:** existing whisper,
  whisper-cli and ffmpeg executables found; existing cache includes multilingual
  tiny/base/small/large-v3-turbo weights. Read installed help and file metadata
  only; no model download/install, hash verification, local ASR benchmark,
  private transcription or capture. This offers a concrete next test toward
  local private-safe intent intake; local transcription alone would not permit
  forwarding private text downstream.
- **Current documentation:** README, acceptance and review dispositions now
  distinguish actual English provider proof, held cases and remaining natural
  input/Spanish/human/latency/corpus gates. Reference/adaptation notes remain
  linked; no deprecated TTS API silently substituted. Full stretch product is
  still not acceptance-ready. Parent checkpoint requested; terminal results
  returned after final local verification/commit and remote CI inspection.

- **Implementation committed:** `65bad7ab3aa09970a25a9546f30266aa4a1cecc6`
  contains speech review repairs, expiry-state clarity, cancellation saturation
  protection and the complete pinned U.S.House5 public-sample contest. Full local
  behavior suites, module syntax and whitespace passed; staged patch inspected
  for credentials/account identifiers and unrelated artifacts.
- **New publication blocker:** automatic approval review denied pushing this
  newer commit to the existing PR6, again citing retained no-publication wording
  and asserting no later user authorization. The command did not execute; no
  retry or alternate publication route used. Original three retries above stay
  completed. PR6 therefore remains atdd6c1ac with its actual green CI; there is
  no remote CI for65bad7a. Exact follow-up approval question requests pushing
  this branch's tested OpenOracle implementation and related logs to existing
  PR6 only, no merge/deploy/secrets/private data. Question tool accepted it but
  returned no request ID. This is pending, not an uncertain push outcome.


### 2026-10-24 08:43 UTC — local natural input, Whisper reuse and latency limits

- **Completed implementation:** supported EN/ES paraphrases/contextual follow-ups
  draft only fixed public operation/language/version fields, with explicit
  confirmation. Typing retains the current checked parent/map; source/challenge
  reuse current owner. Stop/Erase/language clear pending confirmation. First-load
  map initialization defect found in actual browser and independent review,
  fixed to application-owned version plus after-await session fencing. Existing
  exact public queries preserved. Bounded grammar is not general conversation.
- **Completed behavior verification:** provider-off browser natural first
  question → map/journey; Yes/No → typed source follow-up retained original
  explanation; Spanish switch/challenge displayed original and withdrawal;
  Stop cleared pending draft with speakers off. Existing full local Node and
  Python source/job/HTTP suites passed; focused input check rerun after exact
  alias compatibility repair. No test quota, human media or API call.
- **Completed implementation:** new brief generation operation <=260characters,
  unchanged source/numeric/time/attribution/polarity/independent critical checks.
  Request-fit remains critical at .95. Disclosures and whole final waveform ASR
  unchanged. No paid brief result or latency improvement claimed.
- **Completed local reuse:** hash-verified existing tiny/base/small weights and
  installed Whisper20250625; network/download disabled public EN/ES benchmark.
  Tiny/base inference roughly.3/.5s; small1.5–1.6s. All Spanish transcriptions
  had an imperative-word error; tiny also mistranscribed English maps. Added
  optional memory-only bounded local adapter, no capture route/cloud transport.
  Actual base adapter public check.347s load/.569s inference; requires local
  confirmation, rejects pre-cancelled input. No model/package install or private
  speech. Mac result is not Pi memory/throughput or resident-quality evidence.
- **Decision:**33.02s prior English ready time is unacceptable for conversation;
 26.82s reading dominates buffering. Try concise checked units; keep safe text/
  maps immediate. Modern Realtime2.1Mini synthesis is only a possible explicit
  comparison, not requested Live silently replaced or deprecated TTS introduced.
  [Input/latency review](docs/rebuild/INPUT-AND-LATENCY-REVIEW.md) records data flow,
  benchmark limits, official docs, alternatives and unimplemented queue work.
- **Blocked/new — known not executed:** automatic approval review rejected
  launching the specific <=$0.20 Spanish brief text/Live/ASR trial, stating no
  user-authored approval for this run. No paid request/reservation started, no
  retry/alternative. Exact scoped approval question accepted without request ID.
  Shared ledger remains$1.96 conservative reserved/$0.2127044667 estimated usage
  plus earlier unmetered Playground usage, not invoice.
- **Blocked/new — known unattached:** actual Opus5.5High UI verified; eight scoped
  source files/review prompt rendered via installed PeterSteipete Oracle skill,
  dry-run/files report and credential/account scan. Automatic approval review
  rejected external Claude source upload for asserted missing trusted disclosure
  authorization. Attached count0, no send/retry/bypass. Exact scoped approval
  question accepted without request ID. Earlier reviews are not this delta's
  review; local independent review found no remaining consequential issue in its
  bounded pass. Optional adapter was not in the denied bundle.
- **Pending existing:** no retry of denied PR6 push; main-chat approval still
  pending. Local changes will be committed together with these decisions. Remote
  PR/CI remain atdd6c1ac, not evidence for current local work. Full stretch and
  human/multilingual/accessibility/corpus acceptance remain open.


### 2026-10-24 08:49 UTC — local increment committed and independently reviewed

- **Completed:** `59e8ee016f735537e3322e79b7572aaab9c57d91` contains the confirmed
  public-intent flow, bounded brief operation, optional local Whisper adapter and
  input/latency evidence. Staged file scope, credential/account-pattern scan,
  whitespace and changed-module syntax passed. Working tree was clean afterward.
- **Completed:** independent follow-on review found no consequential defect in
  the optional local adapter or exact-alias compatibility. It confirmed no
  capture/server wiring, bounded PCM, verified existing weights, no download
  fallback, local correction requirement and honest cancellation/Mac limitations.
  No API/network/Git/media action occurred in that review. Capture-owner fencing,
  privacy-erasure and device acceptance remain future integration gates.
- **Completed artifact:** local provider-off browser screenshot
  `openoracle-local-input-confirmation.png` retained outside Git; fixed selected
  follow-up is visible with the retained map journey and unchecked speaker
  consent. No Library/Claude transmission or played audio is implied.
- **Pending:** three exact approvals remain unresolved: existing PR6 push, new
  eight-file Claude upload and one <=$0.20 synthetic Spanish provider trial.
  No request ID was exposed for either new question. Denied actions were not
  retried; new upload attachment count0 and provider process never started.


### 2026-10-24 09:17 UTC — broader official notice experience implemented locally

- **Completed recovery/admission:** found the retained official eight-page KCEB
  full sample in the original Hack Midwest archive (SHA92cda731…5dc62), beyond
  the two-page W1-P7 harness. Current KCEB authority page still links it; current
  PDF bytes were not re-fetched and remain labeled October9 snapshot. Fresh
  JCEB original matches the earlier archive (SHA032814e6…64a2); visually reviewed
  both rendered pages and KCEB candidate/judicial pages2–6. Originals/old repo
  unchanged; no personal lookup or restricted SOS retry.
- **Completed implementation:** deterministic compiler reads only pinned PDFs,
  exact candidate/party/instruction spans and page/column-cropped questions. It
  reproduces55 printed contests (34candidate,11retention,10measures),62 candidate
  entries by contest and11 retention entries. These are retained-document union
  counts, not merged person identities, all ballot styles, current certification,
  personalized membership or eligible write-in completeness. NO CANDIDATE FILED
  remains a source status; KCEB's visually absent Senate heading is excluded.
- **Completed implementation:** integrated public-notice chooser with all source
  rows/gaps; exact measure/retention wording and qualifiers; U.S.House context
  retains roster; Proposition A opens official maps. New source-only recap is
  local/optional; suspected-transcription action withdraws the whole selected
  view and links originals, without sending a report or changing admission.
  Extracted presentation uses existing app signal/currentness/hooks, no second
  session/audio owner or paid route. Local composition is labeled honestly.
- **Completed verification:** compiler/pinned fixture reproduced independently;
  wrong two-page sample correctly rejected. Independent review found no
  consequential issue, including component extraction/instruction spans. Full
  existing Node/Python suites and changed syntax/whitespace passed. Browser
  exercised complete District6 roster+office, source recap/withdrawal, county
  filing-status distinction, exact Independence bond amount/terms, and390px
  Spanish Sni Valley wording (50percent/previous-year conditions retained),
  original lang=en and zero horizontal overflow. No human device/audio,
  screen-reader or bilingual civic acceptance is claimed.
- **Blocked source refresh:** one direct official Congress.gov member URL read
  returned failed-to-fetch restricted URL. Stopped that access, no alternative
  route/retry, and did not promote archived member material as new current
  candidate background evidence. Candidate background remains visibly absent;
  campaign excerpt and restricted-source boundaries unchanged.
- **Approval consolidation running:** prepared one local bundle listing exact
  pending PR commit range, refreshed narrow Claude source file scope/destination,
  and at most$0.20 Spanish two-job reservation within shared$200. No denied
  operation was retried. New work has zero paid usage; existing ledger unchanged.
  No merge/deployment, credentials, private voter data or human media authority
  is sought. Main chat owns the consolidated question with Daniel.


### 2026-10-24 09:32 UTC — late office-source repair and exact approval snapshot

- **Completed commit:** `77a2041` implements the55-contest retained-notice browser,
  compiler/provenance, typed presentation, source recap/withdrawal and validation
  above. All writes stayed in the isolated rebuild/task workspace; old source
  originals remain unchanged.
- **Completed root finding/repair:** old showOffice could display a delayed
  source after Stop. Added read-only snapshot() to the existing session owner,
  shared abort/timeout and stale-revision rejection; browsing does not begin or
  reset a second session. Deliberate source requests after Stop use a fresh
  shared controller. No grounding/source threshold changed.
- **Completed actual failure/recovery verification:** provider-off local HTTP
  delayed the public office response. Pending read→Stop showed stopped; releasing
  the late response did not display term text. A deliberate new read succeeded;
  Erase removed the view and speaker consent stayed off. Temporary diagnostic
  server/tab closed. Ordinary current-build browser repeated read-after-Stop
  with all three District6 candidate rows retained. Node regression suite and
  changed syntax/whitespace passed; independent narrow source review found no
  consequential lifecycle regression. No additional test-count target.
- **Completed review preparation only:** refreshed narrow Oracle-rendered bundle
  `openoracle-current-source-review.md`,307129bytes, SHA256
  `6955c310de8625f85336df1f5af268b8458d90e17da5080ff25463be3eee8f59`.
  Contains16 explicitly enumerated relevant application/code/data files, including
  source inventory and session repair; exact file hashes are in the adjacent
  manifest outside Git. Credential/account-pattern scan passed. This replaces
  the obsolete eight-file proposal for approval purposes, not an upload retry.
  No attachment/submission/new Opus critique occurred.
- **Pending consolidated approval:** task-workspace
  `openoracle-pending-approval-bundle.md` names the final exact local commit set
  for existing public draft PR6, the above16-file Claude payload/destination,
  and one at-most$0.20 synthetic Spanish Responses/Decisions→gpt-live-1/
  gpt-transcribe trial within shared$200. No merge/deploy, new access, private
  voter data or human media. No denied action retried; no new usage/reservation.
  Main chat owns the single question with Daniel. Proposed bundle is outside
  Git so it can name the final committed snapshot without a self-reference.
- **Still open:** complete individual ballot styles/current certification and
  write-in eligibility; candidate identity/rights/background coverage; new-measure
  interpretations; broader fresh multilingual input/voice/composition; human
  civic/pronunciation/screen-reader/device and latency acceptance. The current
 55-contest source browser is useful implementation, not full stretch completion.


### 2026-10-24 10:18 UTC — source-bound comprehension and admitted office contexts

- **Decision/completed:** continued independent local implementation against the
  original stretch office/explanation/challenge/optional-teach-back/recap jobs.
  Reused the existing session/abort/audio owner; no new controller or framework.
  Peter Steinberger's installed Oracle guidance remains the actual consulted
  skill (`/Users/danielgreen/.codex/skills/oracle/SKILL.md`); narrow advisory
  review, proportionate behavior checks, no test-count target. MP-codebase-design
  small-interface guidance applied. No new Claude submission or paid inference.
- **Completed source admission (retrieval09:40:54UTC, recorded here as backfill):**
  retained original official https://auditor.mo.gov/aboutus and
  https://documents.house.mo.gov/billtracking/info/howbill.htm HTML, final URLs,
  retrieval/last-modified metadata and hashes outside Git. Deterministic compiler
  retains exact text-node spans and normalized excerpt hashes. New office-context
  fixture SHA319fe5d1a34d91ff3f6abf5ce0989abb5871f28673cb9ab752941821d48bd6b3.
  Generic duties/terms now available for Missouri House/Senate, Auditor duties
  and prior U.S.House context. Auditor source lacks term length: explicitly
  missing. This is institutional context, never candidate performance/promises.
- **Blocked source retention:** Jackson County charter landing/PDF requests
  returned403; Missouri court original HTML download returned403 after readable
  browser research. Stopped those sources; no alternate route/admission. Revisor
  section links redirected home and its public browser endpoint returned a
  server error; no snippets used as admitted term/court evidence. County10
  candidate contests and11 judicial office contexts remain unadmitted. Existing
  denied SOS and restricted Congress.gov requests were not retried.
- **Completed:** all10 JCEB measure questions have exact source reading aids,
  fixture SHAce86fc958df059fecf6969a4f856577051d5c963f830ca9af401d2d81c217a91.
  Full conditions retained (both chambers, sufficient revenue, rate changes,
  prior-year sales-tax revenue, quo-warranto proviso). Full original stays
  visible; highlighted passages are quotations, not generated legal meanings.
  New interpretation-evaluation cases are explicitly unapproved/untested and
  not served by the application; the evaluation route returns404. No new civic
  Yes/No/candidate claims promoted.
- **Completed connected journey:** selected authority/contest/source version
  binds confirmed local natural follow-ups: original, read parts, office,
  optional source-comprehension check, view-only challenge and source recap.
  No raw words transmitted or saved; no vote preference scored/stored. Changed
  selections clear stale drafts. Challenge withdraws the transcription, links
  originals and allows labeled return to the saved transcription without
  pretending correction or staffed reporting occurred.
- **Completed verification:** both compilers reproduced byte-identical fixtures;
  source tampering and cross-item guide/context binding hold. Existing Node and
  offline Python/loopback suites passed. Actual provider-off browser exercised
  Senate four-year/House two-year duties, Auditor conditions/missing term, fresh
  selected-notice confirmations, stale-selection clearing, exact Sni/Amendment7/
  Blue Springs/Independence passages, gentle check feedback/Skip, source recap
  and challenge/return. Controlled delayed guide after Stop remained held while
  original stayed readable; deliberate retry succeeded.503 retained original;
  Erase rejected the pending response and cleared workspace/input/consent. Own
  diagnostic server/tab closed. No human capture/playback or provider request.
- **Review finding fixed:** independent authorized local code reviewer caught
  target-language confirmation comparing against current language. Fixed without
  weakening source binding; actual EN→ES→EN confirmed in browser. Also repaired
  retained old-language status and focus loss during async reading.390px Spanish
  keyboard confirmation retains reading-button focus, Tab reaches condition,
  Skip returns to the summary, original lang=en and zero horizontal overflow.
  Screen-reader, real-device and human bilingual civic/pronunciation acceptance
  remain open. New public screenshots retained in task workspace, not Git.
- **Unchanged external gates:** immutable proposed push remains exactly six
  commits dd6c1ac→8db5221 to existing draft PR6; this later work is excluded.
  Approval bundle SHA5cd2c7ed28ef8c6c1c1ac0ce415d3eccd9444c34b531232fa41a69399b083434
  and16-file Claude payload SHA6955c310de8625f85336df1f5af268b8458d90e17da5080ff25463be3eee8f59
  rechecked unchanged. Denied push/upload/$0.20 Spanish trial not retried. No new
  paid usage/reservation; ledger remains$1.96 reserved,~$0.2127044667 recorded
  usage/duration estimate plus earlier unmetered Playground usage, not invoice.
- **Remaining:**55 printed contests are not individual styles/current certified
  roster or personal membership. Candidate background/source rights/identity,
  county/judicial context, new interpretations, fresh broader conversation,
  checked Spanish speech/acceptable latency, accessibility/human trial and
  renewed actual Opus5.5High product review remain. No full-stretch/public-demo
  acceptance, public deployment, merge, new credentials or Pi changes claimed.

### 2026-10-24 14:12 UTC — approved exact push, measured UI latency and native Chrome comparison

- **User approval/action completed (backfill from13:34UTC remote evidence):**
  Daniel explicitly approved the previously asked push of65bad7a and6d90b11,
  without merge/deployment. Checked remote stilldd6c1ac, then retried the denied
  operation once on that new exact approval using an explicit6d90b11 ref, not
  HEAD. Push succeeded; remote/PR6 head verified
  6d90b11fc66de4294249bf4cb0e3d89efd3dbd76. Both existing CI runs completed
  success:40098712545 and40098709152; push run created13:34:20Z/updated13:34:38Z.
  Later59e8ee0/57c17db/77a2041/8db5221/b10c05b and this increment excluded.
  No merge/deploy, PR publication beyond the approved range or new credentials.
- **Completed local implementation:** memory-only numeric stages now separate
  queue/routing/retrieval, generation, validation, Decisions, Live generation and
  whole-WAV ASR. Live connection/start/instruction/delta/close/finalization marks
  contain no content; an unsent instruction does not get a sent marker. Client
  diagnostics distinguish source/map, checked text, paint opportunity and audio
  readiness. They clear on Erase, reject stale writes, omit arbitrary fields and
  are not persisted as analytics. Human playback/precise pixel visibility is not
  measured or inferred from a delta. Existing waveform/ASR/disclosure gates kept.
- **Completed optimization/evidence:** question, map geometry/pins and legal
  snapshot load concurrently; original-source control no longer waits for
  geometry. Geometry requires admitted question/labels, legal status remains
  fresh/dated. Three cold provider-off browser samples on identical retained
  assets with150/350/550ms controlled delays: original source526–539ms→156–163ms,
  verified maps526–539ms→367–377ms, full view1089–1101ms→558–566ms. Paint proxy
 545–561ms→163–180ms. Warm sample/source0.4ms/map0.9ms/paint26.2ms still waited
  for legal recheck; full567ms. Normal loopback source14.1ms/map30.3ms/DOM34.5ms,
  paint42.8ms. Not API, internet, Pi, human or p95 evidence. Saved reproducible
  provider-off benchmark driver and numeric report; no prerecorded answer cache.
- **Independent review finding fixed:** parallel legal read could expire while
  geometry waited. Shared mapStatusCurrent predicate now runs at fetch admission
  AND immediately before constructing the displayed claim; existing expiry
  replacement retained. Fake-clock boundary proof and independent re-review
  closed finding. Catalog preserves existing mappings/validateLayout and checks
  current revision after each await. Source/prompt-injection/whole-WAV/cancel
  proofs still pass. Only meaningful owner clock/stale/privacy checks added;
  installed test-audit guidance applied alongside prior Oracle/engineering skills.
- **User direction/completed actual native comparison:** Daniel requested native
  ChatGPT genUI on connected Chrome. Used two dedicated Temporary chats with
  public map URLs and exact public Sni Valley wording only, visible Medium
  setting; backing model not exposed. No private files, code upload, memory/
  inbox request, account upgrade, credentials, microphone or sound. Applicable
  OpenAI Docs/native-visualization guidance and supported CUA browser controls
  used; Apps SDK/Atlas skills checked and not misrepresented as native-Chrome
  testing tools. No new browser package/remote-debugging access installed.
- **Native map result/failure/recovery:** first generated inline artifact visibly
  failed at runtime. Native text admitted unavailable parsed geometry but called
  artifact functional; client error disproved that claim. One repair produced
  working EN/ES and region selectors plus official links, explicitly no geometry
  or zoom. Clicked Spanish/KC; ArrowRight moved focus and Space selectedSt.Louis.
  No map/synchronization was invented or inferred. UI-reported work1m4s/17s is
  not independently measured full latency; polling interleaved with local work.
- **Native source-card verified:** original full English with prior-year sales-
  tax-revenue qualifiers; Spanish interface, full condition highlight, original
  source details, optional membership-comprehension feedback, Skip and keyboard
  Reset exercised. Reset restored English/no highlight/details/check/feedback.
  Native showed an unreviewed Spanish translation; it was NOT imported/admitted.
  UI work label18s, not independent TTFT. Screenshots retained outside Git; actual
  controls were operated. No internal renderer/network/persistence or human
  screen-reader quality is inferred from observed DOM/AX behavior.
- **Applied reference patterns:** closed local renderer catalog (no arbitrary
  generated HTML/JS, extra renderer inference or framework rewrite), stable
  source-loading shell, progressive source version details. Original links and
  critical freshness caveats remain visible; details opening halts speech through
  the existing owner. Compared matching OpenOracle source/map interactions,
  equal viewBoxes/KC maps, gentle check/Skip,390px Spanish open-version-details
  without overflow and full reset clearing source/timings/input/consent. Native
  code not copied. Exact prompts, why/how/files/licensing limits recorded in
  GENERATIVE-UI-COMPARISON.md and DEMO-REFERENCES.md. Open-source alternatives
  considered, not installed or performance-benchmarked; no private native API
  inferred. No React/runtime migration or broader civic claims added.
- **Costs/remaining approvals:** zero new app API calls/reservations. Shared
  ledger unchanged$1.96 reserved/~$0.2127044667 recorded usage/duration estimate
  plus earlier unmetered Playground usage, not invoice. Authorized native UI
  interactions use existing ChatGPT account allocation; no API-price inference.
  Previously denied Claude payload and Spanish paid trial were not retried.
  Immutable approval files kept unchanged as historical exact targets; narrow
  push approval does not approve their full six-commit range or later localwork.
  A new minimal latency proposal is≤$0.11 reserved for one English Luna brief+
  Decisions then conditional same-owner Live/full-WAV ASR (two jobs/fourrequests,
  no retry/capture/Play). Requires applicable new approval and fresh price/account
  checks; not a vendor hard-dollar guarantee. No paid test executed here.
- **Next/open:** concise actual-provider timing, safe independently meaningful
  speech units/queue and persistent-connection/model comparison remain unproven.
  33.02s prior long-reading preparation remains unacceptable, not solved by UI
  timings. Full candidate/styles/current certification/rights, broader semantic
  genUI, natural multilingual speech and human civic/accessibility/device/latency
  acceptance still open. Normal updated local review8917; old8914 process could
  not be stopped through its expired tool handle (unknown process ID), no process
  enumeration/alternate kill attempted. Own diagnostic servers closed after QA.
  No public-ready claim, denied-source retry, human media, merge/deploy or Pi work.

### 2026-10-24 14:16 UTC — native comparison reading-width repair

- **Completed local milestone:**0f452ee records the measured latency/native UI
  increment above. It remains unpushed, outside Daniel's exact two-commit grant.
- **Observed/fixed:** current screenshots showed normalized official wording
  stretching across the full inventory card. Applied a76ch maximum reading
  width,1.075rem text and1.6line spacing to original-wording only, following the
  native card's bounded reading-column concept. No source text, highlights,
  interpretation, palette, controller or provider behavior changed; no code copied.
- **Actual verification:** desktop quote width823px within1116px source area,
  line height27.52px; full exact question/qualifiers retained.390px viewport with
  version details expanded has no horizontal overflow and unchanged question
  ending. Captured/inspected fresh screenshot. Proportionate browser inspection
  and whitespace check; no redundant behavior tests added for CSS-only change.
  Human reading/screen-reader/civic acceptance remains pending. No paid/media/
  external action; original repository and immutable approval files unchanged.

### 2026-10-24 15:00 UTC — KC sample journey, source integrity and renewed review

- **User direction/authority, backfilled from trusted task history:** Kansas
  City is the polished main demo; a second verified Jackson County ballot must
  demonstrate actual local/jurisdiction differences. Preserve the original full
  stretch target. Daniel's later live-call approval authorizes the English
  <=$0.11 and Spanish <=$0.20 trials within the shared $200 total, scrubbed
  OpenOracle review in the existing Claude Opus5.5High chat, newer pushes and
  merge/deploy after appropriate checks with rollback notes. Updated AGENTS.md
  precedence. This supersedes earlier no-merge/deploy permission, not source,
  privacy, credential, human-media or spending safeguards. Original approval
  timestamps were not supplied here; this is a backfill, not invented chronology.
- **Completed source work:** visually inspected both retained W1-P7 PDF pages;
  original SHA256 d33d41b4c377e7d9d1bd63af0c2f1053bc4b63f608eb3167200a8385e576e0fc.
  New reproducible compiler emits25 contests:8 candidate elections/15 printed
  names,11 retentions,6 measures, with exact column/page spans and reading hashes.
  Initial arithmetic sanity assertion used16 names and failed; corrected to15
  after recounting all eight printed contests. No partial fixture was admitted.
  Final fixture SHA256690a32a8df2b24ccec68fb6d725f469a9467a7ce8ba76cfc1c74244cbb39323e.
  The eight-page KCEB notice remains distinct from this two-page sample.
- **Completed integrated behavior:** main candidate shortcut opens the actual
  KC context; a direct county comparison opens the JCEB Independence bond
  original, including$19,900,000/20-year plan/1827 Log Courthouse. The UI explicitly
  says the JCEB notice is not a second individual style and does not assign
  another contest alongside it. All25 KC contests are selectable. The55-contest
  notice union excludes sample occurrences; all source contexts preserve gaps,
  originals, dates, no ranking and no personal membership. Existing one-owner
  session/speech lifecycle reused, no second controller.
- **Source blocker:** official JCEB public on-the-ballot page exposes the notice;
  its individual sample lookup requires name and DOB. No private lookup was
  submitted and no supported second individual public style was established.
  A notice comparison is implemented without claiming the requested second
  individual ballot is complete. No denied SOS/Congress/county/courts access retried.
- **Actual browser findings/fixes:** the new plain candidate shortcut initially
  failed the older exact router. Added bounded EN/ES aliases and regression cases;
  both now reach the view. Exercised KC House5's complete three-name roster,
  county source change, Spanish controls and390px no-overflow rendering. Language
  remount clears selection; map journey now returns to the same public source/
  contest. Original wording/challenge/check/recap use their matching source.
  Idle reset was observed clearing the review while other work ran; deliberate
  re-entry restored the demo. No microphone or Play was activated.
- **Independent review:** existing review agent reproduced the pinned compiler,
  checked source/context/tamper/routing bindings and reported no substantive
  finding within its scoped code review; it did not claim human/currentness proof.
  Installed Oracle (@steipete), test-audit, original planning, PDF and official
  OpenAI docs guidance applied. No redundant test quota or framework migration.
- **Actual Claude review:** existing chat displayed Opus5.5High. Uploaded a narrow
  eight-file source/public-transcription bundle after Oracle files report/render
  and sensitive-pattern scan, SHA25618624d1b8a95197a7b805dc7bf0ec7fca5d2846cbd00e5c0037a60b40524b6c4.
  Returned critique found compiler omission/order assumptions, missing fiscal
  text in the journey original, contradictory PropA gap copy, uncomputed browse
  version and smaller source/Stop/navigation/accessibility problems. Fixed:
  bounded heading/instruction/Write-in regions, all-row/anchor accounting,
  source-derived order/names and rejection of unexpected/status rows; full PropA
  wording plus artifact/page/prefix parity; returned runtime combined source
  digest; actual record dates/mark publisher; strong candidate list text; stopped
  load copy and same-source return. The speculative missing brief operation is
  disproved by current Python/JS operation registries. Fresh generation remains
  scoped to the question sentence; the source view now includes its fiscal note.
  Seven-file focused fixes bundle SHA2560ddb5894ec5ef4d65735ad8dcd2b11d39a733282bb674598b0f8be52697846f5
  submitted for re-review; result pending at this entry. Original frozen approval
  bundles remain unchanged. Only relevant app code/instructions/public text sent.
- **Verification completed:** provider-off Node/Python suites, new source-region
  owner proof, served-route/privacy contracts, syntax and whitespace pass. Tests
  show altered sample rejection, no foreign ballot/question leakage, actual
  printed order and unknown-row holds. Browser confirmed PropA->official maps->
  complete original with fiscal sentence->same-source return. These checks do
  not establish heard speech, bilingual civic quality or public readiness.
- **Costs / exact new blocker:** fresh official pricing checked. Existing API
  credential presence checked as a boolean only, no secret extraction. Platform
  billing redirected to sign-in; automatic approval review denied selecting the
  intended existing Google account, stating the exact account/sign-in action
  was not authorized. Known not executed; exact sign-in-only approval requested,
  pending, with no request ID returned. No alternative account/route attempted.
  Neither approved trial started or reserved. Shared ledger unchanged$1.96 in
  conservative reservations/~$0.2127044667 recorded usage-duration estimate plus
  two earlier unmetered Playground calls; no fresh balance/invoice assertion.
  Claude used the existing account allocation; no subscription/purchase/new access.
- **Artifacts / running / next:** local providers-off review8922. Saved current
  full-page KC review image to Library and persisted its local identity; no
  private browser/payment content included. Renewed review running; focused
  commit/newly authorized push and remote CI verification next. Known remote
  rollback checkpoint remains6d90b11fc66de4294249bf4cb0e3d89efd3dbd76 with previously
  passed CI. Current source rights/current certification, second individual
  style, candidate evidence, semantic composition, consolidated recap, accessible
  map description and real bilingual/latency/human-device gates remain open.
  Merge/deploy are authorized but not performed: current server is loopback-only;
  safe hosting/protected metered inference and publication acceptance are not yet
  established. Do not equate permission or passing mocks with showcase readiness.

### 2026-10-24 15:05 UTC — review closure and idle privacy repair

- **Completed returned critique:** actual Opus5.5High focused re-review marked all
  eight initial findings closed in its attached scope, with full product gates
  still open. Fixed residual application-label wording and a per-notice PropA
  pointer that could falsely say missing transcription was above. Definite
  pre-dispatch HTTP errors now restore only the local allowance;5xx/transport
  uncertainty stays uncertain. Existing owner cases prove both outcomes.
- **Found/fixed:** independent follow-up caught sourceSelection surviving idle
  erase, which could reveal the previous public source selection to the next
  visitor. Cleared it in idle erase and pagehide; explicit Erase/language already
  clear it, and BFCache restoration resets. Same-session map return/Stop retain
  it intentionally. Independent re-review closed the lifetime defect by code
  inspection; real120s browser proof began15:05:17Z with JCEB Independence and
  remains running at this entry. No fake clock, shortened production timeout,
  test-only seam, visitor identity or paid inference introduced.
- **Validation:** changed transport owner cases and syntax/whitespace pass after
  residual fixes; full provider-off Node/Python checks had passed the integrated
  source increment. Final remote CI will exercise all checks on the pushed code.
