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
