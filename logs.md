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

### 2026-10-24 15:11 UTC — actual idle failure and first-return guard

- **Completed local commit:** fd34825 contains the KC/source/review increment.
  No new push yet; do not expose a known session-lifetime defect for convenience.
- **Actual failed proof:** at15:07:33Z, the JCEB selection set15:05:17Z was still
  displayed after more than120s; re-opening candidates preserved it. Therefore
  the first real idle check did not pass. Background timer suspension/returning
  focus ordering is a plausible mechanism, not a measured browser-internals fact.
  Code inspection confirmed activity unconditionally touched the idle clock
  before a delayed interval could erase the session.
- **Fixed:** one existing-owner eraseSession path now serves explicit Erase and
  interval expiry, clears source selection and suppresses idle autofocus. Capture-
  phase activity checks expiry before touching. Includes direct click for
  assistive inputs without pointer/key events; expired actions are consumed
  before old controls can renew a turn. Independent review identified that
  direct-click path before this final repair. No new controller or fake clock.
- **Actual partial verification:** explicit Erase followed by candidate entry
  starts kc-sample with empty contest. Final real120s idle check began15:11:20Z
  with JCEB Independence; outcome still running at this entry. No human/AT/media
  proof inferred from automation. Syntax/whitespace pass.
- **Read-only hosting assessment:** no deployment configuration found in scoped
  experimental/docs/workflow files, and connected Vercel's repository-filtered
  project read returned no match in its available account scope. This does not
  prove absence on other hosts/teams. No hosting project, access, credential or
  billing change created; a safe metered deployment target remains unestablished.

### 2026-10-24 15:26 UTC — traced idle feedback loop and verified erasure

- **Diagnosis/correction:** earlier background-clock theories were not confirmed.
  Installed MP-diagnosing-bugs guidance applied to the actual failing browser
  loop. Temporary tagged logs recorded numeric clock values and event types only.
  They showed the100s warning reveal causing two automatic scroll events, which
  the generic scroll activity listener counted as input. That renewed the clock,
  hid the warning and prevented120s expiry. No unexpected begin/reset or private
  input was needed. The actual source/clock/event evidence, not the initial
  theory, determined the fix.
- **Fixed:** passive scroll no longer renews the session. Actual wheel, pointer,
  key, focus and click input remain; a stable EN/ES Continue button gives an
  explicit accessible extension path. Focus within that warning does not hide
  its control or renew merely by landing there; activation renews and returns
  focus to the reading workspace without scrolling. Warning copy no longer
  promises generic AT scrolling extends time. Expired-input capture guard and
  shared erase remain. Repeated identical live-warning text is not rewritten.
- **Actual real-clock proof:** Chrome last input15:22:44.827Z; automatic erase
  recorded15:24:45.546Z (~120.719s). Fresh AX state showed Session cleared,
  empty question/workspace and no source controls; deliberate re-entry showed
  kc-sample/empty contest, not prior JCEB Independence. This fixes the observable
  original failure. No shortened timeout, clock injection or human/AT assumption.
- **Cleanup/validation:** all temporary OO-IDLE-QA logs removed, core.mjs back to
  unchanged bytes, default debug capture/export remains off. Node checks and
  syntax/whitespace pass. Independent review closed capture/erase ordering and
  identified the warning-focus issue repaired above. Final Spanish warning/
  keyboard check began15:26:37Z; outcome pending. No new API reservations/costs,
  human media, credentials or public deployment. Focused privacy commit next.

### 2026-10-24 15:30 UTC — pushed code, remote CI and final review artifact

- **Completed:** fd34825 and b8f9009ac53456dd378e0b4e9a8773adfeb86277 plus the
  earlier seven local source/input/latency commits pushed normally to existing
  draft PR6 after fresh explicit approval. Remote branch was verified unchanged
  at6d90b11 before push; no force, merge or deployment. PR description rewritten
  around actual current behavior, evidence, costs and unmet stretch requirements.
- **Remote verification:** both offline-contracts runs completed SUCCESS on
  exact code SHA b8f9009ac53456dd378e0b4e9a8773adfeb86277:
  https://github.com/daniel-p-green/open-oracle/actions/runs/40107057655 and
  https://github.com/daniel-p-green/open-oracle/actions/runs/40107062980.
  This is the latest CI-passed code checkpoint for rollback/reference, not an
  assertion that the full product is accepted. Earlier6d90b11 remains in history.
- **Actual Spanish warning proof:** after its real100s warning, keyboard focus
  remained on visible idle-continue; Enter hid the warning, focused workspace
  and retained the active JCEB Independence reading. Independent final review
  closed warning focus/renewal and confirmed temporary logs absent. No human
  screen-reader, acoustic or civic-language acceptance inferred.
- **Deliverable:** current full-page KC source-flow image updated in Library
  preserving its identity/version guard; local metadata application succeeded.
  Dedicated Chrome local8922 tab retained, duplicate agent-created in-app tab
  closed. Pending Platform existing-account sign-in tab retained for handoff.
  No personal/payment screenshot was delivered or uploaded.
- **Still blocked/pending:** exact billing account-selection approval remains
  unanswered; automatic review denied that action and it was not retried. Both
  newly approved bounded API trials remain unstarted/unreserved, with ledger
  figures unchanged. Source admission still lacks a second individual JCEB style,
  current certification/write-ins and candidate background; full semantic UI,
  unified recap, fresh bilingual latency/heard quality, accessible map description
  and human/device acceptance remain open. Hosting read found no matching repo
  project in the available Vercel scope; no safe public metered endpoint/rights
  release exists yet. Merge/deploy permission is present, readiness is not.

### 2026-10-24 16:19 UTC — one consolidated evidence recap and recovery

- **Direction/boundary:** parent confirmed exact Google sign-in question is
  pending in main chat; no retry or alternate balance route. Continued independent
  recap/evidence work. The earlier1067-dollar observations remain historical,
  not freshly verified credit. No paid test/reservation started in this work.
- **Source discovery completed, gap remains:** one focused official JCEB search
  plus current on-the-ballot/sample-ballot page reads still establish only the
  November3 notice and name/DOB individual lookup. No public November individual
  style established, no query submitted, no guessed URLs/person/district combo,
  no denied SOS/restricted-source access retried. Notice is still never relabeled
  as the requested second individual ballot. References:
  https://jcebmo.org/election-information/on-the-ballot/ and
  https://jcebmo.org/sample-ballot/ .
- **Implemented actual recap:** one existing app owner now combines current-
  language checked journey units and up to six explicit source/contest/version
  choices in one panel. Source Add and global My recap are different actions;
  browsing saves no recap source. No raw input, votes, teach-back answers, account,
  storage/export or provider transmission added. Deduplication/bounds/version/
  occurrence/URL/kind checks keep mixed candidate, retention and measure cards
  source-specific. Source content re-resolves against pinned records on open;
  names/party/instruction/status/full question/original/version/gaps retain roles.
  The two original private recap renderers were replaced, not a new controller.
- **Architecture:** recap-view.mjs owns presentation/typed source resolution;
  experience.mjs retains state, shared session/abort/current-ticket/erasure.
  Closed card variants compose the selected evidence without arbitrary HTML/JS
  or any rendering LLM call. This is deterministic user-chosen composition, not
  a claim of full AI-planned generative UI. Existing checked-unit integration is
  wired; no new live-provider combined-unit browser result is claimed.
- **Actual browser proof:** browsing->empty recap; explicit KC House5->complete
  three-name card; explicit JCEB Independence->second exact question card with
  $19,900,000/20-year plan/1827 Log Courthouse; withdrawal removes that occurrence;
  Spanish navigation/removal and original English preserve traceability. Close
  returns to the connected originating control. Real120s idle erase of the two
  explicitly saved sources left next recap empty. Explicit Erase also cleared.
- **Actual fault proof:** isolated providers-off loopback wrapper returned503
  and delayed /kc-public-sample.json. Failed content withheld with working Remove
  all saved sources; no unchecked partial roster appeared. Stop during actual
  Checking source versions hid the panel and late response stayed suppressed;
  deliberate reopen recovered. Erase while loading plus late release left the
  new recap empty. No shortened timeout, fake clock, API, microphone or playback.
- **Review:** existing independent reviewer found no substantive issue in its
  scoped code pass. Actual Claude Opus5.5High setting verified; Oracle-scanned
  app-only bundles rendered/reported before upload. Initial SHA256
  9a2416ca6f4012936e6bd031a87cb7beffbf3dcd20c46da46153af8d3bdc4f7b;
  focused fixes a056b2d96fb7fb42ba78703284ac11b827405429c6091a0d377a569c19322d60;
  shared-terminal closure67826c8595bc3dd4a9b8871fe638eda837eda6365d4dea73c45d29764d0e4eeb.
  Returned findings fixed: per-unit AI/not-quotation/human-pending labels;
  withdrawal follows actual kc-sample dependency rather than matching a notice
  label; failure removal, Add error recovery and original-opener focus. Follow-up
  returned all five closed. Review code/runtime limits remain explicit.
- **Official next steps:** anonymously retained verified KCEB voter-status and
  JCEB sample-lookup pages, original HTML outside Git under
  ../ballot-research/authority-nextsteps, retrieval timestamps/hash/requirements
  and navigation-only role. Fixture SHA256
  af7758008f478eca9b5a5b6878e7cc2e8817975bd0827809e5944da34fcf7ae0.
  No names/DOB/lookup/results used. Model review caught private-tab residue risk
  on a shared terminal. Chose conservative plain-text references for a resident's
  own device, with private-input/Erase limits and two-jurisdiction scope. No new
  operator mode/access framework; no lookup anchors/forms/window opening. Public
  original-PDF evidence links stay separate. Final actual re-review closed both
  remaining findings; loading/failure copy now consistently says references.
- **Observed/fixed viewport issue:** Chrome retained actual1014px despite390px
  request, so that attempt is not mobile evidence. Actual390px in-app browser
  exposed617px overflow from expanded hashes. Scoped recap-details wrapping fixed
  it: scrollWidth375 with full hashes and question qualifiers retained. No new
  CSS behavior test quota; actual fresh visual/DOM inspection used. No actual
  phone/Pi or human AT/Spanish civic/pronunciation proof is implied.
- **Validation/costs:** final provider-off Node/Python, static-route/privacy,
  source/context/version/tamper, syntax and whitespace checks pass. Added one
  recap owner boundary proof, extended existing intent proof; tests target changed
  invariants, not counts. Installed Oracle/test-audit/engineering guidance applied.
  Fresh local ledger read still$1.96 conservative reservations/~$0.2127044667
  recorded usage-duration estimate plus2 earlier unmetered Playground requests;
  not invoice/current credit. No new OpenAI call, credentials, paid grant, external
  human message, merge/deploy or Pi modification. Claude used existing allocation.
- **Running/next:** local review8923 providers off; prior owned8922 stopped via
  valid handle. Temporary fault server8924 will close after QA. Focused commit,
  PR6 push/remoteCI, artifact and final receipt next. Source completeness/candidate
  admission, second verified individual style, AI-planned composition, live
  bilingual latency and human civic/AT/device/release gates remain open. No
  showcase-ready claim or fabricated coverage fills those gaps.

### 2026-10-24 16:30 UTC — recap push, remote CI and artifact receipt

- **Completed:** pushed focused implementation `004e618e7e535421859ebb9b0ec97b7826b507f1`
  to existing draft PR6. Both remote offline-contracts runs succeeded with that
  exact head SHA: https://github.com/daniel-p-green/open-oracle/actions/runs/40111326672
  and https://github.com/daniel-p-green/open-oracle/actions/runs/40111329385 .
  No merge/deployment. Prior `b8f9009` and `dd2c76e` remain rollback checkpoints.
- **Artifact completed:** verified unclipped in-app-browser full-page capture,
  saved to Library as `openoracle-consolidated-recap-review.jpg`, ID
  `libfile_9df65636d3f88191afca6247ec64dcb0`, version0; local identity metadata
  applied successfully. Earlier Chrome full-page capture was clipped, so it is
  not the delivered image. Actual returned Opus closure messages26/28 retained
  outside Git. No private account/billing screenshot or voter record included.
- **Cleanup:** owned temporary fault server8924 stopped using its valid handle.
  Providers-off review8923 stays running. Dedicated app/billing tabs marked for
  delivery/handoff; no sign-in/account selection retried and no API trial started.
- **Remaining:** exact existing-account selection question remains pending in
  main chat after automatic review denied that action; no request ID was returned.
  Second JCEB individual style remains a source gap after public official page
  inspection. Recap/local composition are demonstrated technical progress, not
  full stretch or public-demo acceptance. Fresh checked bilingual latency,
  AI-planned composition, candidate admission and human civic/AT/device/source-
  release gates remain. Keep the existing ledger; no incremental paid usage.

### 2026-10-24 16:53 UTC — evidence contracts preserved; voice-first correction

- **Implemented, not accepted product UX:** bounded Proposition A evidence
  composition selects admitted component IDs in the existing Responses call;
  no additional rendering call/factual props/HTML/URLs. Mandatory original and
  uncertainty survive selection. Exact checked text remains the speech input.
  Provider-off task-specific plans explicitly withhold fresh AI text. This is
  supporting infrastructure, not a natural voice agent or completed stretch UX.
- **Verification:** provider-off Node/Python suites passed after environment
  recovery. Actual pre-disconnect browser checked full original/fiscal wording,
  map-reference focus and source/limits compositions. Isolated, visibly labeled
  synthetic provider harness exercised model-shaped selection, unsupported
  candidate_ranking hold and Erase. It performed no API call or device media.
  Independent review found cross-language retained-unit use and late answer
  erasing independent reading activity. Fixed both; actual synthetic browser
  proved local fallback after EN→ES and preservation of expanded source/focus
  when delayed Spanish text arrived. No live model/latency claim.
- **Failure/cleanup:** environment disconnected during390px inspection; outcome
  and viewport reset remain unknown, so no new narrow-screen evidence claimed.
  Executor recovered; old session handles cannot resume because executor key
  changed. Bounded loopback checks confirmed both8923/8924 refuse connections;
  no stale server assumed running. Browser/computer tools are currently absent.
- **Denied/pending:** automatic review denied upload of the scrubbed seven-file
  bundle to existing Claude Opus5.5High chat, saying trusted sharing authority
  was absent. SHA25632a9ae0f3d259315c90c8a1b580835609bce6bd88550c1cd5f93989daec137bc,
  112646bytes, ../openoracle-evidence-composition-review-20261024.md. No retry,
  indirect route or successful review claimed. Existing billing-account
  selection remains pending separately; no sign-in or credential creation.
- **User correction accepted:** Daniel rejects the document/recap-led UX as an
  interaction-model mismatch. Stop auxiliary expansion. Primary interaction must
  be Start talking, EN/ES, actual connection/mic state, captions and focused
  model-driven visual canvas, with evidence/recap/diagnostics progressively
  disclosed. Original PRD connected adaptive live voice remains the target.
- **Billing clarification:** boolean-only check confirms existing API key present;
  no value extracted. Existing successful test scripts establish prior explicit
  organization/project headers. A fresh browser billing login is not technically
  required by the API; earlier balance1067.97 and shared200 cap/reservation1.96
  exist. Reuse only the established server-side credential/scope under current
  authority; do not bypass the denied login or call historical credit current.
  Live loop still needs implementation and actual synthetic public input tests;
  human microphone/speakers remain unapproved. No new paid run in this increment.

### 2026-10-24 17:13 UTC — native voice-first implementation; paid test denied

- **Preserved:** evidence contracts2b3cac8 pushed toPR6; independent review
  closed its two wiring repairs. Daniel explicitly rejected the recap/document
  UX. Natural spoken conversation, contextual follow-ups and model-selected
  visuals are the primary interaction; support panels are not product acceptance.
- **Implemented, not live-proven:** default preview now centers Start talking,
  EN/ES, connection/media state, caption and focused canvas. Human capture/player
  absent and labeled. Source review requires review-tools. Existing session,
  request/job/cancel/ledger/checked-text/map owners reused. Native gpt-live-1
  receives only hash-checked synthetic public PCM; native gpt-6-luna Decisions
  selects view/map focus/delivery. Grounded Responses+independent Decisions
  precede Live speech, buffered/ASR-checked. No arbitrary factual UI props,
  HTML/URLs/geometry, vote advice or personal assignment.
- **Docs:** fetched official voice-websockets, live-delegation, decisions-voice,
  voice-server-controls pre-playback checks, and September pricing changelog.
  Live0.05/minute, backend extra. No output-done event or commentary exactness
  guarantee assumed. Quiet+planned transcript only proposes a segment, not
  completion approval. Turn-named decisions and effective-config acknowledgement
  fence the second input.45s operation timeout includes backend/ASR/connection,
  plus<=15s graceful close. Final usage/close_requested required for success.
- **Review/fixes:** independent fake transport exposed0.05s checked versus0.15s
  emitted PCM being accepted. Fixed growth during ASR and post-seal audio; one
  protocol regression now covers positive, extra during ASR/close and missing
  usage. It passed4.168s, no network/media. Legal status has expiry and Stop
  demotion. Browser tools still unavailable: no new visual/mobile/provider result
  claimed. Provider-off preview8923 restarted; open_in_codex queued its tab.
- **Synthetic inputs only:** installed local TTS generated4.640s public question
  and3.088s map follow-up to files, no speakers. Initial sandbox output was empty;
  length/integrity admission caught it before inference. Scoped local generation
  then succeeded. These are caller fixtures, not a substantive answer library.
- **Denied, known not executed:** ../native_voice_bounded_trial.py would reserve
  <=0.10 within shared200, one Live session/up to two public inputs, bounded
  Responses/review/ASR; no human media/new key/retry. Automatic review rejected:
  "Runs a live paid OpenAI voice trial using an existing credential and reserves
  $0.10, but the trusted instructions require approval for paid API calls and no
  such user approval covers this exact request." No request ID; do not retry
  without new relevant approval. Verified no output/native-loop ledger row;
  reservations unchanged1.96, no new usage. Claude upload remains separately
  denied; billing account selection separately pending.
- **Blocker clarified:** existing credential and earlier successful account-scope
  headers exist. Fresh billing login is not an API authentication prerequisite.
  No denied-login bypass/alternate credential/new access used. Earlier1067.97
  remains historical. Real native compatibility, measured latency/interruption,
  EN/ES, human consent/privacy/input/player and recording/acceptance remain open.

### 2026-10-24 17:27 UTC — actual native trial held; transcript contract implemented

- **Approval reconciliation:** parent supplied direct API-budget/optimization
  instructions and Claude source-only approval as materially relevant evidence.
  Retried known-not-executed native test once under normal review. Initial
  launch failed before reservation/API because system Python lacked websockets;
  verified existing .api-test-venv has pinned15.0.1 and used that established
  runtime without install/new credentials. Billing login was not retried.
- **Actual test, held:** one gpt-live-1 session connected at1568.561ms; native
  Decisions selected measure/unchanged at7531.189ms. Grounded gpt-6-luna brief
  passed source/review at11114.138ms and actually selected explanation/original/
  uncertainty components. These are test-origin offsets, not first audible
  latency.45s deadline held before checked speech; graceful close finalized at
  47654.160ms. One native decision, no accepted audio segment, no second turn,
  no human capture/playback or persisted output audio. Do not call this a live
  conversation success, UI-render proof or latency improvement. Private public-
  input receipt preserved at ../native-voice-en-trial-01-private.json.
- **Cost evidence:** actual reported43.0Live seconds plus Responses/review usage
  gives0.0361289333 usage/duration estimate, not invoice. Shared reservations2.06,
  cumulative recorded estimate0.2488334 including this run; older unmetered
  Playground requests remain outside that estimate. No credit purchase/reload,
  balance reauthentication or changed200 cap.
- **Correction implemented, not provider-verified:** native delegation docs use
  commentary.append to return the backend result. First adapter used instruction
  only. Now sends checked commentary plus exact-reading instruction, while still
  checking actual buffered speech/ASR rather than assuming verbatim output.
  Added numeric bytes/transcript-length/match diagnostics; no raw input transcript
  retained/exported. Cannot retrospectively diagnose the first run's exact spoken
  mismatch from diagnostics it did not collect. Offline PCM regression passes.
- **Further test denied, known not executed:** same runner under existing test
  runtime, another<=0.10 bounded experiment after this substantive protocol fix,
  was rejected: "This would initiate another paid $0.10 OpenAI voice experiment
  after the explicitly authorized one retry already ran; the available
  authorization does not cover an additional paid run." No request ID, no retry
  or alternate route. Exact next approval is one additional0.10 native experiment
  with the same public clips, established credential and caps. This is separate
  from the still-pending billing login. No second reservation/API call started.
- **Latest user acceptance:** live voice + language-appropriate on-screen
  transcripts + generative UI. Implemented provisional timed input versus checked
  text versus final audio transcript states, shared language/source/turn/revision,
  explicit no-playback label and ephemeral erasure. No delta/delegation called a
  final input turn; unmatched timestamp windows withhold input captions. Output
  final labels require full checked session completion, not text generation.
  Actual EN/ES conversation, input finality, frame synchronization and assistive
  acceptance remain open; translated navigation is not proof of these outcomes.
- **Other limits:** current native code needs renewed Opus5.5High review; trusted
  scope addresses the former rejection but browser tools are unavailable, so no
  upload retry/review claimed. Accidental unrelated read-only lookup changed
  nothing; no returned contents copied to the project. Continue only project
  work. No merge/deploy/readiness claim or Pi changes.
  No merge, deployment, Pi change or full-product success claim.

### 2026-10-24 17:43 UTC — corrected native speech checked; follow-up held

- **New exact approval and actual action:** Daniel explicitly approved the
  corrected<=0.10 native experiment and reaffirmed the shared200 test maximum.
  Normal tool review permitted the corrected test using only the established
  server credential/scope and existing synthetic public clips. No billing login,
  microphone, player, new credential or software installation. Preserved the
  second receipt outside Git at ../native-voice-en-trial-02-private.json.
- **Measured partial result, overall held:** connected709.586ms; native measure
  decision6738.327ms; checked text9896.239ms; candidate speech segment at22955.855ms;
  independent ASR matched24317.470ms; turn2 began24363.681ms after effective config
  acknowledgement; native maps/kansas_city choice28321.554ms. The second fresh
  answer held journey_language_match_held and voice_segment_incomplete. Session
  finalized33277.555ms with30.0 reported Live seconds. One checked audio segment,
  two native decisions, zero human-heard/playback/rendering claims.
- **Cost:** corrected run recorded0.0265864 estimate from token/duration usage,
  not invoice. Shared conservative reservations2.16; cumulative recorded direct
  estimate0.2754198. Earlier two unmetered Playground requests remain excluded.
  Sanitized stage/cost evidence committed in
  docs/rebuild/NATIVE-VOICE-TRIALS-2026-10-24.json, with receipt hashes and explicit
  missing code-snapshot provenance; no account identifiers/private voter data.
- **Findings and fixes:** first answer196characters required12.9s waveform.
  Reduced brief maximum260→120 in server and client without changing factual,
  source, language or ASR checks; effect unmeasured. Timing diagnostics showed
  only16 of23 input fragments aligned, leaving an incomplete provisional second
  caption. Keep unmatched fragments withheld and no final input claim. Added
  bounded numeric window diagnostics and a public-fixture-only diagnostic
  provider in the external trial runner to investigate the language hold; no
  production payload recording or threshold weakening.
- **Independent local re-review:** closed idle-expiry and lost-final-caption
  defects. Activity capture erases expired content before renewal; passive scroll
  no longer renews and Continue keeps stable focus. Coalesced provisional events
  preserve essential checked events; final receipt carries revalidated canonical
  checked payloads. Server cannot mark a failed native session ready. Extra PCM
  during ASR/close and missing final usage remain holding conditions. Scoped
  independent inspection found no further consequential defect; whole-product
  acceptance and renewed Claude review remain open.
- **Verification:** JS contracts passed; Python non-socket contracts passed.
  Sandbox denied loopback bind in HTTP setup, so reran only existing HTTP suite
  with normal scoped escalation: all HTTP checks passed. No paid/media calls in
  checks. Actual viewport/mobile/AT validation unavailable with browser tools.
- **Denied, known not executed:** next diagnostic .api-test-venv/bin/python
  native_voice_bounded_trial.py, same two public clips/credential,<=0.10 reserved,
  was rejected by automatic review: "This would launch another paid $0.10
  OpenAI voice test after the explicitly approved corrected run already executed;
  no trusted user authorization covers this additional experiment." No request
  ID; no new reservation/call. Stopped this operation, no alternate route. Exact
  next approval: one diagnostic native run<=0.10 on those same inputs/scope,
  no human capture/playback. Separate denied billing login remains untouched
  and is not technically required for API authentication.
- **Remaining gates:** native two-turn completion, input timestamp/finality,
  actual Spanish voice, acceptable measured safe-output latency, human consent
  and private-speech handling, device interruption, full browser interaction/
  recording, source/rights/coverage gaps and Opus5.5High native-code critique.
  No merge, deployment, Pi change or showcase-ready claim.

### 2026-10-24 17:46 UTC — native increment pushed; exact code CI passed

- **Completed:** commit8ca6697d0f79e6fb178ff5e3de20b00222ca1dca pushed to the
  verified existing rebuild branch/draftPR6; no merge/deploy. Purpose and actual
  trial/acceptance limits replaced stale PR claims, including correction that
  fresh billing login is not technically required for the existing API credential.
- **Remote verification on that exact code:** both offline-contracts succeeded:
  https://github.com/daniel-p-green/open-oracle/actions/runs/40117562213 and
  https://github.com/daniel-p-green/open-oracle/actions/runs/40117557762 .
  CI is provider-off and does not establish live or human acceptance.
- **Local artifact:** restarted providers-off http://127.0.0.1:8923/ with current
  native voice-first modules and pinned map assets. HTTP read verified current
  root/module bytes and disabled providers/fixture dispatch/mic/playback; browser
  rendering remains unverified. No new screenshot or interaction recording.
- **Outstanding blocked actions:** next synthetic diagnostic paid launch denied
  before execution as recorded above; browser-control capability unavailable for
  primary interaction QA and renewed existing Opus5.5High source-only review. No
  alternate credential/login/review route, unapproved media or deployment used.

### 2026-10-24 18:17 UTC — offline caption diagnosis and actual primary-UI replay

- **Scope:** denied paid diagnostic remained paused, no retry/alternate launcher,
  new credential, billing login, media, publication or extra API spend. User
  stepping away does not resolve a tool denial. Reused debugging, frontend QA
  and Peter Steinberger test-audit guidance for high-value behavior checks.
- **Language evidence limit:** saved run2 contains23 input deltas/16 displayed
  timed fragments but no rejected raw fragments/windows, held second draft or
  predicate scores. Cannot establish true language mismatch versus false
  positive offline. Existing .95 critical language/factual gates unchanged;
  extended the existing owner proof so isolated negative language review still
  holds even when other predicates pass. Public-only diagnostics are prepared
  in the external bounded runner, which was not executed.
- **Concrete caption repair:** official native schema measures start/end from
  session beginning, not sent PCM count. Removed that invalid clock equivalence.
  Synthetic audio commands carry owned IDs; only echoed matching IDs with valid
  timing attach provisional words. Missing/invalid binding marks unavailable and
  persists a gap label; known prior IDs cannot contaminate a current turn.
  Echo is optional in the API: actual coverage still unverified, not declared
  fixed. Protocol proof covers unknown IDs with plausible old timing, valid IDs
  with differing clocks and missing timing after an accepted partial.
- **Actual Chrome1002x757 UI replay:** browser control returned. New local replay
  adapter/committed public-only event fixture reuse the real jobs/HTTP/session/UI
  path, no provider instance/key/shared ledger/API/player. Explicit offline
  banner/status; historical reviewed text/audio omitted rather than minted into
  a current success receipt. Observed measure→actual paired KC maps, selected KC
  buttons, two separate provisional EN turns, Stop legal demotion and language
  erasure/Spanish labels. No relevant console errors or horizontal overflow in
  that desktop state. Actual inputs remain incomplete/provisional.
- **UI repairs:** Spanish skip/sample/visual accessible labels; stopped pending
  captions become held; pending source display no longer spins after Stop; new
  session no longer displays Session erased. Remember local map view across an
  unchanged model focus; retained maps keep original/source context. Source hash
  wrapping uses overflow-wrap. These are focused primary interaction fixes.
- **Responsive limitation:** Chrome viewport override returned unchanged1002px
  then inconsistent300px/scale through scoped CDP. Cleared overrides/restored
 1002x757; no390px or physical mobile proof claimed. No persistent browser
  setting or security permission changed.
- **Independent review:** found missing-timing gaps bypassing unavailable state
  and map Stop preserving geometry before original/source controls. Fixed both:
  gap admission covers all unbindable fragments, source controls mount before
  optional legal IO. Re-review closed both by inspection. Broader provider-off
  Node/Python/loopback checks passed; focused protocol/map/client checks passed
  after repairs. No test count used as quality or live-acceptance claim.
- **New denied browser check:** additional same-origin replay Stop-before-map
  scenario targeting http://127.0.0.1:8925/ returned "Host access is restricted by
  policy." No completed scenario proof; setup/tab outcome uncertain, no retry
  or alternate browser route. Earlier completed replay evidence remains scoped.
- **Claude scope clarified:** actual Opus5.5High visible in fresh tab for the
  existing OpenOracle review conversation. File-chooser APIs timed out before
  setFiles, second attempt reset UI tool. No native bundle attachment or prompt
  sent, no model critique. Native-app lookup selected an unrelated window and
  was not operated. Did not change extension permissions. Final source-only
  native v2 bundle193186bytes/SHAbee77e8c…20cd4 outside Git;17files+instructions,
  no account/credential/private data. Earlier frozen payloads untouched.
- **Single next approval plan:** docs/rebuild/NATIVE-VOICE-NEXT-TEST-SPEC.md
  requests up to4 distinct synthetic native trials, <=0.10 each/<=0.40 aggregate
  reserved inside existing200. Existing account/credential; public EN pair,
  installed-voice synthetic ES pair, named-repair verification and one recovery
  goal. Max45s operation+15s close, capped calls, no automatic retries; uncertainty/
  denied action/auth/scope/cost/closure failures stop sequence. This is planning
  only; reservation is not a vendor dollar hard cap. Current shared reservations
  remain2.16, recorded direct estimate0.2754198 excluding older unmetered calls.
- **Next:** normal authorization for that bounded sequence; resolve local host/
  file-chooser capability without new access; actual returned native-source
  Opus review; then measured full EN/ES caption/voice/map behavior. Human media,
  source/style/rights coverage, accessibility and showcase acceptance stay open.

### 2026-10-24 18:20 UTC — caption/UI repair pushed; remote gates verified

- **Completed:** focused code/fixture/plan/log commit
  590d124e61fcf6f6f7a41033cb9288674e1ed4cb pushed to existing draftPR6. Both
  exact-code offline-contracts succeeded:
  https://github.com/daniel-p-green/open-oracle/actions/runs/40120164963 and
  https://github.com/daniel-p-green/open-oracle/actions/runs/40120161134 .
  PR description now distinguishes actual offline rendering, unverified live
  correlation, the specific Claude attachment failure and pending0.40 sequence.
- **Still paused:** denied paid diagnostic, later host-policy-blocked browser
  scenario, native-source Opus attachment/review. No new spend, human media,
  access grant, merge/deploy or showcase-ready claim. Existing frozen external
  payloads and historical receipts remain unchanged.

### 2026-10-24 18:49 UTC — actual native-source review returned; bounded sequence approved

- **Completed review:** existing Claude conversation returned Opus 5.5 High
  critiques in Messages30/32; selected model/High verified in UI. Source-only,
  no reviewer execution. The custom attachment dialog required Upload from
  computer before the supported chooser; earlier chooser timeouts had submitted
  nothing. No permissions changed or duplicate submission. Source bundles SHA256
  bee77e8c94008c6e488a9b692ece3d98070cc70aac8af1a9efa6ab740bb20cd4
  and 50536b73c1a664fbc10704d263ad3171ed1e83bdfeb89ccefd494d999ad65a21.
- **Disposition:** implemented fixture-only public draft/predicate diagnostics,
  operation/language/prior tags, per-turn stage timings including input end and
  first voiced buffer, distinct deadline/cancel outcomes, and a held-speech note
  alongside retained evidence. Production operational payloads stay unchanged.
  Runner serializes after asyncio.run returns, including finished worker calls.
  Retained post-seal audio hold and 45s+15s close bound; did not adopt suggested
  70s expansion or discard extra speech. First rejected extra chunk is a lower
  bound, not total extra speech. Map speech/visual parity remains an open defect;
  diagnostic keeps that path stable to identify the earlier language hold.
- **Verified offline:** focused public diagnostic, native protocol, budget/jobs
  checks pass, including no sensitive transport fields retained, package bounds,
  uncertain prior usage stop, and internal deadline held versus operator cancel.
  This does not verify live behavior or current browser rendering of the note.
- **Approved, not yet running:** parent relayed Daniel's exact live approval of
  four synthetic voice trials <=0.40 aggregate/<=0.10 each within shared200.
  Existing credential/account, public EN/ES clips, no human capture/playback.
  Atomic ledger now enforces purpose uniqueness, four rows, aggregate ceiling
  and final usage before another reservation. Reverified official pricing:
  Live0.05/min, Luna0.10/M input and0.50/M output, transcribe0.0045/min.
  Reservations remain conservative estimates, not vendor dollar hard caps.
- **Still held:** separate billing login, human media, local-browser scenario
  denied earlier, product acceptance and deployment. Fresh login is not required
  for established credential. Next: one normal approved EN diagnostic dispatch,
  inspect real drafts/scores/stages/usage before any later package stage.

### Backfill — 2026-10-24 18:50:50 UTC English diagnostic receipt; repair recorded later

- **Completed:** approved package English diagnostic native_voice_9cd29d593732f2f7,
  finalized close_requested,8s reported Live usage. Direct estimate0.0068188667,
  reservation0.10 retained; no invoice or fresh balance claim. Native measure
  selected7.502s, input completed6.613s, generation returned10.024s. Draft172
  chars exceeded brief120, so deterministic hold before review/audio acceptance.
  No output playback or persisted output PCM. Earlier language hold not reached.
- **Caption finding:**13 native input deltas, zero command-bound fragments;
  current provider run did not echo a usable client_event_id. Input marked
  unavailable, no guessed timeline binding or complete caption claim.
- **Repair:** user request already said120 but developer instruction said700.
  Aligned instructions and added structured-output minLength/maxLength120 for
  brief,700 for other operations. Official structured-output docs support these
  constraints for the standard model; no reviewer threshold relaxed.
- **Independent finding/fix:** terminal usage alone did not prove closure before
  next package stage. Persist explicit trial_closure_confirmed, require it plus
  final usage before next reservation, and test usage-only finished row blocks.
  Existing EN row confirmation backfilled only from its actual final receipt.
  Focused jobs/journey/public-diagnostic checks passed. No new paid dispatch yet.
- **Next:** distinct repair_verification purpose, same EN pair and unchanged
 45s operation envelope. Any unconfirmed usage/closure stops the sequence.

### Backfill — 2026-10-24 18:52:35 UTC repair receipt; subsequent local repair

- **Completed:** repair_verification native_voice_2dbceff673d2a8c6 finalized with
  orderly close and8s Live usage, direct estimate0.0069573667, reservation0.10.
  Schema respected120 but draft ended in "and". Independent entailed0.60,
  no_additions0.88, request_fit0.75; language0.97. Genuine incomplete explanation
  held, no accepted segment. This does not diagnose the older turn2 language hold.
  Generation2.014s, independent review1.289s; native decision0.128s after delegation.
- **Repair before next distinct stage:** brief request now one complete sentence,
  target90/hard120 characters, central attributed congressional approval question,
  omit secondary clauses. Reject a missing sentence ending/trailing conjunction
  deterministically rather than relaxing review or stretching accepted text.
- **Closed review finding:** independent re-review confirms explicit final
  closure package gate fixed. Two package slots consumed; no repeat English
  verification authorized under the purpose-unique package. Spanish and recovery
  remain distinct optional stages, pending offline repair proof and valid usage.

### Backfill — 2026-10-24 18:54:11 UTC Spanish receipt; subsequent local repair

- **Completed:** installed Paulina es_MX generated approved public question files
  locally at24kHz mono16bit,5.131s and3.228s; verified bounds/hashes, no playback.
  Spanish native_voice_84fd8388ce235c6b finalized orderly,7s Live usage, estimate
 0.0059872333. Native measure selected7.349s, generation1.522s. Fresh Spanish
  rhetorical question lacked explicit source attribution; deterministic
  journey_sentence_attribution held before independent review/audio acceptance.
  No claim of bilingual completion or false-positive repair.
- **Local repair:** prompt now explicitly requires naming the question as source
  in the requested language, with Spanish attribution stems and preserved
  conditional approval. Guard/threshold unchanged; existing regression includes
  observed un-attributed Spanish form and an explicitly attributed form.
- **Next:** recovery purpose remains the fourth/final package slot: cancel when
  checked text is reported, verify no segment released and orderly usage close.
  If grounding holds first, report recovery as not reached rather than success.

### Backfill — 2026-10-24 18:55:25 UTC recovery receipt; package reconciliation

- **Completed:** recovery native_voice_34c0cfe1215a90cd finalized orderly,7s Live
  usage, direct estimate0.0061315333. Complete brief passed factual checks
  (entailed0.98,no_additions0.95,polarity1.0,language1.0) but request_fit0.74
  held. Checked-text cancellation trigger was never reached: requested=false,
  no accepted segment. Do not report a recovery/cancellation pass.
- **Package terminal:**4 distinct purposes consumed,0.40 reserved, measured
  duration/token direct estimates0.025895 combined, no invoice confirmation.
  Shared reservations2.56; cumulative recorded estimate0.3013148 excludes older
  unmetered calls. All four orderly final usage/closure confirmed. No output ASR
  request or accepted audio in this package; no repeat package slot/new paid run.
- **Honest limitation:** no successful full EN/ES loop, second-turn map or input
  caption proof from this package, no improved safe-audio latency measured.
  Native routing succeeded; deterministic/independent holds prevented release.
- **Execution error/fix:** the new Spanish offline positive fixture failed on
  singular "congresional" but the sequential shell continued to a passing second
  test; English recovery launched before that first result was inspected.
  English test did not depend on the Spanish phrase, but validation sequencing
  was wrong. Corrected guard to accept singular/plural congresional(es), without
  accepting unrelated scope. Rerun complete offline checks before commit.
- **Next local work:** preserve public evidence/metrics, review semantic-fit
  contract and measured bottlenecks with actual Opus feedback; no threshold
  lowering or fabricated live success. Current product remains not ready.

### 2026-10-24 19:05:51 UTC — bounded trial findings reviewed and offline repair verified

- **Timestamp clarification:** four preceding trial completion times are
  backfilled from immutable receipt filesystem completion timestamps; repair/
  reconciliation actions followed and are not assigned invented execution times.
- **Actual Opus Message34 returned:** selected Opus5.5High verified. Finds brief
  contract misalignment and omission of legislative origin, not proof a lower
  reviewer threshold is safe. Shared BRIEF_REQUIREMENTS now define generation
  and request-fit; actor/conditional/congressional meaning required; included
  names exact, title/county/fiscal details explicitly left for follow-up.
  Schema200 permits a clean overlength hold; accepted brief bound remains120.
  Spanish source attribution also accepts plantea/consulta; congressional scope
  accepts singular/plural. Live outcome of these latest fixes is unverified.
- **Financial containment:** web ProductPipeline and CLI reject native fixture
  activation after package consumption; provider-off replay remains separate.
  Budget closure now derives from sanitized receipt finalized/close_requested
  and exact matching metered usage, not caller boolean. Later finish bookkeeping
  preserves prior evidence. Existing four rows updated only from their receipts.
- **Verification:** final Python provider-off suite passed with scoped loopback
  binding permission; initial sandbox invocation could not bind mock servers.
  Node suite and diff whitespace check passed. Independent reviewer inspected
  final contract/closure/web-route delta and found no substantive regression.
  These are offline/code checks, not successful live voice or human acceptance.
- **Original product direction:** reread all363lines of original stretch PRD
  and voice-first brief; reviewed final October11 video production transcript
  and12timestamped frames without audio playback. Hasheddeliverable/prerecorded
  limitations recorded in PRIOR-DEMO-REVIEW.md. Latest user asks adaptation from
  explicit requests/understanding, never education/accent inference. Finite
  acceptance matrix prepared in existing DEMO-ACCEPTANCE.md, no new features.
- **Official API roles rechecked:** managed Agents API is documented at
  /v1/agents/sessions but no managed job run/account eligibility claim; background
  trial deferred. GPT-Live native Decisions chooses bounded actions; Responses
  generates grounded text; independent Decisions and waveform ASR gate release.
  Actual newest calls prove access to used live/text/decision services, not
  end-to-end readiness. No new credentials, billing login or human media.
- **Next:** focused core commit, then original-demo/matrix documentation commit;
  explicit new adversarial Opus request against immutable snapshot and actual
  held evidence. Earlier Message34 already complete, no duplicate in-flight send.

### 2026-10-24 19:06:21 UTC — original-demo acceptance reconciliation

- **Completed core commit:**64972f2 records actual held trials and tested local
  fixes; no full voice success claimed. Original repositories/video unchanged.
- **Prepared documentation increment:** existing acceptance matrix now has16
  stable requirement IDs tracing original stretch/JTBD through implementation,
  actual evidence and remaining gates. Added verified API roles and explicit
  managed-Agents not-executed status. PRIOR-DEMO-REVIEW.md records the actual
  final video SHAedd3497a…d7b69, production-transcript/frame-only review, design
  patterns and simulated/prerecorded limitations; DEMO-REFERENCES.md links why/how.
  No separate new feature scope, copied movie code or API demo license assumption.
- **Next:** commit this bounded reconciliation, use the immutable combined
  snapshot for the expressly requested adversarial Opus5.5High review, fix proven
  findings and update existing PR6. No new paid trial under consumed package.

### 2026-10-24 19:21:40 UTC — adversarial findings returned; local repairs verified

- **Actual result:** explicit adversarial source bundle297774bytes/SHA911bd678…
  b5ec38 of immutable57fd509 submitted once asMessage35, Opus5.5High visibly
  selected. Message36 returned not-ready with severity/concrete references/repro
  steps and proven-vs-hypothesis-vs-missing distinctions. Review artifact is
  docs/rebuild/CLAUDE-ADVERSARIAL-2026-10-24.md; no reviewer execution claimed.
- **Fixed locally:** retain completed job ID/token for server revocation on
  Stop/Erase, ignore old callback cleanup; Stop doesn't turn finalized captions
  into held captions; explicit repeat reuses only this session's last ASR-checked
  payload/view and rechecks fresh buffered speech without a new text generation;
  remove dead source-check branch; add narrow brief approval/legislative-origin
  omission guard and pre-approval amplitude counter. No review threshold lowered.
- **Verified:** offline transport-after-ready revoke, existing server caption
  removal, protocol fresh explanation→exact repeat with one generation/review,
  checked-text cancellation, late/changed audio, missing usage and deadline paths.
  Final provider-off Python and Node suites pass; independent reviewer inspected
  repairs and found no substantive fault. New browser/human/native-provider
  behavior is unverified. An intermediate protocol test edit had indentation
  error, corrected before final validation/commit.
- **Not adopted:** phase-only caption arrival ownership (late old-turn risk) or
  playback before independent ASR (weakens pre-hearing guarantee). Map speech
  parity, per-turn language switching, reliable input captions and conversational
  safe-audio latency remain open. Corrected review's claim that newest held
  drafts were checked text; no such event occurred in those trials.
- **Completed remote:**64972f2 and57fd509 pushed to existing draftPR6; exacthead
  offline CI succeeded40123925101 and40123929659. PRbody updated actual holds,
  costs, original-video/matrix and remaining gates. New local repair commit next.
- **Budget unchanged:** fourtrial0.40 reservation consumed; estimated0.025895.
  Shared reservations2.56/200, recorded direct estimate0.3013148 excluding old
  unmetered calls. No new paid inference, billing login, human media or deployment.

### 2026-10-24 19:40:07 UTC — follow-up review defects repaired; map navigation aligned

- **Returned actual Opus Message38:** mostly holds, new medium Spanish stem
  defect and low cleanup/repeat/highlight/wording issues. It withdrew its earlier
  held-draft-as-checked-text timing claim. Review remains source-only.
- **Repairs:** natural aprueban/legisladores/lawmakers forms; shared opaque
  revocation lease retains failed cleanup for deliberate Erase retry, coalesces
  pending cleanup and blocks new session until confirmed; truthful local/server
  cleanup labels. Empty repeat clarifies; matching validated map view stays
  mounted. Repeat retains original checked map region to bind identical words.
  Renamed amplitude-chunk metric, corrected fixture/text hash comment and
  no-checked-audio status. Independent review caught Stop cleanup leaving Run
  disabled; availability update now precedes retained-conversation branch.
- **Speech/UI parity repair:** map-display action now uses exact region/language
  navigation acknowledgment, not a new generic measure explanation. No generated
  boundary/legal/personal-district assertion; substantive geographic answers
  remain unsupported. Strict client text/region binding rejects forged map prose.
  Actual provider/browser parity still unverified, acceptance row stays open.
- **Offline evidence so far:** natural Spanish admission, actual shared lease
  failed-then-explicit-retry/stale ownership, native protocol map→repeat and
  first-repeat clarification pass, alongside changed/late audio/usage/deadline
  gates. Final suites/re-review/commit next; no new paid inference.
- **Paid scope:** four approved trials remain consumed/held. Added one proposed
  minimal four-request EN/ES text-contract check <=0.01 in existing spec only,
  with exact per-run limits/expected outputs/stop conditions. Not authorized,
  queued or executed. Each historical hold classified without asserting every
  guard caught false facts; older language hold still unknown.

### 2026-10-24 19:41:42 UTC — final local repair checks passed

- **Completed verification:** current complete provider-off Python/loopback and
  Node suites pass; diff whitespace check clean. New Stop recovery wiring remains
  source-inspected, not a current browser proof. No model/human media call.
- **Remote prior increment:**104c7db pushed; exact-code CI succeeded
  https://github.com/daniel-p-green/open-oracle/actions/runs/40125017596 and
  https://github.com/daniel-p-green/open-oracle/actions/runs/40125014349 .
- **Next:** focused current map-navigation/cleanup/Spanish repair commit,
  immutable narrow source-only Opus follow-up, push/CI verification and report
  the still-open end-to-end/caption/language/latency gates without lowering them.

### 2026-10-24 19:53:00 UTC — final source follow-up and bounded text preflight

- **Returned actual Message40:** Opus5.5High source inspection says repairs hold
  in substance/no unsafe release path found. Still not product acceptance. Added
  closed St./SaintLouis equivalence for its hypothesis; exact expired-owner409
  cleanup handling for real recovery defect; first-map unchanged→statewide;
  retained-cleanup-aware language button and more natural Spanish navigation.
  Focused normalization/lease/brief/protocol checks pass. Lexical brief guard is
  only a presence backstop; semantic/polarity/request-fit review remains required.
- **Parent direction:** check original explicit200 API testing authority through
  normal tool review before asking Daniel another tiny approval. Prepared fixed
  EN/ES brief runner: four requests maximum, one0.01 reservation, existing key/
  account, gpt-6-luna Responses/Decisions only;6KB pre-dispatch payload bound,
 512 outputs per generation, no media, tools, background, retry or new access.
  Offline serialized requests4801bytes generation/3934–3936review. Not executed
  yet. New normal denial would stop it; no alternate launcher/bypass.
- **Remote:**21a5e55 pushed, both exact-head offline-contracts pass40126538052 and
 40126533700. No newly paid call beyond completed fourvoice package at this entry.

### 2026-10-24 19:58:06 UTC — normal review rejected new text dispatch; no execution

- **Denied:** .api-test-venv/bin/python text_contract_bounded_trial.py, four
  fixed public EN/ES text requests/0.01 reservation under existing200 cap.
  Automatic review: new paid external test outside specifically approved
  fourtrialvoice package; broad200 cap alone does not authorize additional spend.
  CreateProcess rejected, known not executed. No pending requestID returned.
  Verified ledger: zero new text rows, reservations2.56, recorded estimate
 0.3013148 unchanged. No retry or alternate route attempted.
- **Concrete next approval:** docs/rebuild/API-TEST-APPROVAL-BUNDLE.md proposes
  one staged bundle covering text and subsequent voice/named repair/recovery,
  maximum6runs/52attempts/0.42 reserved inside200, fixed public data/account,
  prerequisites/stop conditions/no human media/no newaccess. Planning only; no
  approval received or execution queued. Earlier0.01 request not re-launched.
- **Independent work:**74635eb source fixes committed; push in progress/check
  outcome before retry. Existing provider-off/normalization/lease/protocol checks
  passed. Old Chrome8925 host-policy denial remains separate and unbypassed.

### 2026-10-24 20:00:49 UTC — latest source push verified; paid scope remains blocked

- **Completed:**74635eb pushed to existing draftPR6. Both exact-code checks
  passed:40127513264 and40127508941. No merge/deployment. Existing original
  HackMidwest/Pi repositories remain unchanged.
- **Unchanged paid state:** all4 voice trials terminal, no accepted audio in
  that package, recovery trigger not reached;0.025895 estimated/0.40 reserved.
  New text launch denied before execution, zero text rows/reservations added.
  Parent has exact one-bundle proposal in API-TEST-APPROVAL-BUNDLE.md; new
  package must be separately authorized/enforced, never reopen/reset old rows.
- **Still open:** true multi-turn EN/ES audio+captions+generative UI evidence,
  per-turn language switching/context, safe useful audio latency, map geographic
  interpretation, private-safe human capture and primary browser/human QA.
  Host-policy-denied localhost8925 check remains un-retried. No credit-login
  bypass, new credentials, human media, unbounded ingest or public readiness claim.

### 2026-10-24 21:08:55 UTC — exact staged verification authorization received

- **Approved:** Daniel replied “yes approved” to the exact six-run, 52-attempt,
  $0.42 reserved bundle within the existing $200 cap (parent
  Sentinel_861f4223f7ac81919bf442fcf4cdbf44; reply
  Sentinel_09d54ca8577c81918b3000c61c826579). Existing account/credential and public
  synthetic inputs only; no human media, new access or billing login. This is
  materially new authority for one normal retry of the known-not-executed text
  launcher, not a workaround for the earlier denial.
- **Implemented before dispatch:** distinct staged ledger package with atomic
  aggregate runs/reservations/allocated-attempt ceilings, unique purposes,
  per-dispatch text counter, prerequisite and repair-basis checks, uncertain
  response/closure barrier. Old four-trial package remains exhausted/unchanged.
- **Verification:** existing budget-owner boundary checks plus one staged
  lifecycle case pass: missing metered response blocks next stage, premature
  voice blocked, dispatch cap enforced, six allocations total52/$0.42. These are
  temporary local ledgers, no API requests. Installed MP-diagnosing-bugs,
  test-audit and OpenAI Docs guidance read/applied. Official pricing re-fetched;
  relevant Luna/Live/Transcribe rates unchanged. No fresh balance/login claim.
- **Next/running:** fixed text-contract check first; semantic hold pauses for
  diagnosis, unknown usage stops sequence. No provider request has run yet at
  this entry. Focused code commit will pin this envelope before dispatch.

### 2026-10-24 21:17:16 UTC — staged dispatch still denied; independent caption repairs

- **Denied, known not executed:** one normal retry of
  `.api-test-venv/bin/python text_contract_bounded_trial.py` after exact bundle
  approval. Automatic review states: “This executes paid external API requests
  using an existing credential; although narrowly capped and limited to public
  synthetic data, no trusted user approval for this new staged bundle is present,
  and the original user explicitly required approval before paid API calls.”
  No pending request ID returned. Verified zero new package rows/text artifacts,
  reservations2.56/recorded estimate0.3013148 unchanged. Stopped paid sequence;
  no retry, alternate launcher, credential or billing-login route. This is an
  authorization-propagation blocker despite parent-relayed exact approval.
- **Implemented offline:** optional synthetic input-ASR captions bound to the
  exact submitted PCM hash/turn, same-language final-state validation and
  slow-poll recovery. Runs alongside response work; does not replace evidence,
  infer clock offsets, or enable human capture. Off by default; no live or
  current browser success. Source: current official file-transcription guide
  confirms gpt-transcribe original-language text/languages JSON; no forced hints.
- **Independent reviewer findings/fixes:** malformed native usage could still
  authorize another stage; cancelled to_thread ASR could lose metering; staged
  voice counters were allocation-only. Now malformed/unknown usage prevents
  closure, ASR metering occurs inside its worker even when awaiting coroutine
  is cancelled, unsettled ASR blocks progression, and provider HTTP/ASR plus
  Live/native dispatch hooks count attempts. Staged closure requires nonzero
  attempt count exactly matching metered stages. No staged native launcher has
  run; existing old package stays closed. A slow in-flight request cannot be
  unsent, so full reservations remain and uncertain outcomes stop progression.
- **Verified local behaviors:** exact synthetic input caption ownership;
  wrong-language hold; cancellation prevents final-caption/audio release;
  cancelled-await worker still records transcription cost; input final replaces
  provisional/gap events and survives slow polls; malformed usage/ASR settlement
  and dispatch caps block subsequent stages. Existing protocol/job/client owner
  checks pass. No test count used as a quality claim.
- **Skills:** actual installed Oracle (@steipete) and test-audit read; test-audit
  provenance is an OpenClaw adaptation, not a claim of individual authorship.
  Evals-start routed to validate-evaluator: no expert-labeled calibration set
  exists, so model .95 thresholds remain uncalibrated and no TPR/TNR or false-
  positive rate claimed. This does not relax deterministic or independent gates.
- **Next:** immutable focused commit, narrow source-only Opus5.5High review,
  fixes for substantiated findings, push/CI. Existing Chrome8925 host denial
  remains separate/unretried. Full natural EN/ES/visual interaction, context-
  preserving language switch, safe latency and public readiness remain open.

### 2026-10-24 21:19:42 UTC — independent settlement recheck and required local gates

- **Returned review:** independent reviewer rechecked its three findings and ran
  the focused no-network budget/protocol proofs, including cancelled-await ASR.
  No further consequential defect found. The old manual native launcher remains
  closed-package/no-hook; a future approved staged launcher must pass the budget
  dispatch hook before native execution. No such launcher or paid run is active.
- **Verification limits:** broad provider-off Python checks passed apart from
  two test-server class setups denied by default sandbox loopback bind. The
  scoped existing server contract suite then passed with normal sandbox approval
  for a temporary loopback listener only; this does not retry the separately
  host-policy-denied Chrome8925 inspection. Complete Node contracts passed.
  No source changes occurred during these verification runs. Current browser
  transcript rendering and real provider language/caption quality remain unrun.
- **Next:** source-only Opus5.5High re-review of immutable caption/settlement
  increment, then focused fixes if warranted. Full readiness remains false.

### 2026-10-24 21:22:04 UTC — new Claude attachment denied; no submission

- **Committed:** dc06828 enforces approved staged envelope;39c0a12f86727511667e9da4c850a60edb9cb662
  implements optional synthetic caption/usage-settlement repairs. Current local
  contracts passed with the scoped loopback permission noted above; independent
  review rechecked and closed its three concrete findings. No new paid request.
- **Prepared immutable source-only review:** openoracle-caption-settlement-39c0a12.md,
 196842bytes, SHA351bde4fdcd93e83bdd98614ba3ae81187766d00f79e66149f702cb00570c4bb,
  nine exact tracked source/test files plus their diff and relevant review
  instructions. Excludes ledger, keys/account identifiers, private voter/human
  data, unrelated documents and credentials. Destination is the existing Claude
  OpenOracle review chat4c378210-7251-4026-9a90-700a23bc34d3, whose selected UI
  actually showed Model: Opus5.5High.
- **Denied:** supported file-chooser/setFiles attachment action. Automatic
  review: “This uploads an internal OpenOracle source bundle to an external
  Claude session; no trusted user authorization specifies that payload and
  destination, so the sensitive-code egress must be denied.” No retry/alternate
  host/paste route. Verified new attachment count0, composer empty, Send disabled;
  closed unchanged Upload dialog. No new review message or critique returned;
  preceding actual M40 remains the latest completed Claude review.
- **Blocked:** normal approval must recognize the already relayed exact staged
  API permission and source-only Claude permission before these separate actions
  can execute. No pending request IDs supplied. Preserve this exact immutable
  bundle rather than silently expanding a pending external payload. Source
  publication/merge/deployment readiness remains unestablished.

### 2026-10-24 21:23:07 UTC — focused push denied; remote remains unchanged

- **Denied, known not executed:** `git push origin HEAD:rebuild/openai-web-slice-20261024`
  to existing public OpenOracle draftPR6. Automatic review states: “Pushing
  commits to the remote is an external repository publication/commitment, and
  the trusted task instructions explicitly prohibit repository publishing; no
  later trusted user authorization revokes that restriction.” This contradicts
  the later parent-relayed project push/merge/deploy permission but remains a
  tool denial; no retry/alternate publishing route. No pending request ID.
- **Read-only verification:** ls-remote confirms remote branch still
 6fdfb9112b8df6356df27adf3a2e8f00e4579a81. The focused staged-envelope/caption/
  settlement fixes and denial record are local commits only, not current PR6
  code or CI evidence. No merge/deployment. Local worktree clean before this log
  entry. Preserve rollback history/original repositories.
- **Parent handoff:** resolve normal approval for three exact targets: approved
  text launcher/six-stage bundle; immutable196842byte nine-file source-only
 39c0a12 Claude attachment in existing Opus5.5High chat; local commits to existing
  PR6 branch. No cost/access/data-scope increase. No claim that another user
  budget statement is missing; automatic review is not recognizing the relayed
  authorizations. Independent local review closed the material code findings;
  new actual Claude/live/browser acceptance evidence remains blocked/unrun.

### 2026-10-25 01:47:37 UTC — continuation approval recognized for text and PR6

- **New direct authority:** Daniel approved continuation after the parent named
  the blocked staged test, immutable Claude source attachment and intended PR6
  push. Retry each known-unexecuted action once normally; no scope/cost increase.
  Rechecked clean worktree0ce1743, zero staged rows, unchanged immutable source
  bundle351bde4f…c4bb. Official Luna/Live/Transcribe rates re-fetched unchanged.
- **Completed:** exact fixed public text launcher ran normally. Run
  public_brief_contract_ae672bb4ad394621, code0ce1743,3requests, all3 metered,
 0.01 reserved, estimated0.0003821 (not invoice). English accepted after generation
  and independent review at3027.639ms from run start; no voice latency claim.
  Spanish generated123characters including “vigente”, held first as
  journey_time_drift before review because
  ballot wording does not establish current legal status. Correct hold, not a
  false-positive excuse to loosen the guard. Shared reservations2.57, recorded
  cumulative estimate0.3016969. Sequence paused for the allocated named repair.
- **Repair:** generation instruction now explicitly distinguishes source
  “existing” from current legal force; use existente/anterior, never vigente/
  actual/actualmente. Deterministic time check unchanged. Existing brief-owner
  proof covers exact observed Spanish failure and shorter permissible wording.
  The first new positive fixture was still121characters and failed the length
  guard; corrected it to120 before any paid repair dispatch. The earlier commit
  recorded a pass prematurely; the following correction records actual evidence.
  Conditional text_repair slot retains4requests/
 0.01 reservation; no automatic repeat or exhausted-purpose reset.
- **Completed remote:** prior four local commits pushed to existing draftPR6;
  remote exacthead0ce1743 with both offline-contracts checks successful. No merge
  or deployment. The source-only Claude bundle remains unchanged/unsubmitted:
  current tool inventory exposes no CUA/browser executor, so supported-route
  retry is unavailable, not a new content rejection or reason to use a bypass.
- **Reference:** parent is reviewing the newly supplied YouTube benchmark;
  no observations inferred and no duplicate video research performed here.

### 2026-10-25 — text repair result; language-isolated native prerequisite

- **Completed actual text_repair:** public_brief_contract_3eadf5cd8133fcf1,
  code4ba6206,3requests/0.01reservation/0.0003904 estimated direct cost. English
  independently accepted at2455.644ms; Spanish correctly removed vigente but was
 121characters, held at existing120 engineering limit before review. No Spanish
  review or acceptance claimed. Both text-purpose slots are consumed; no text
  purpose reset or implicit repeat. Combined new estimate0.0007725,0.02reserved.
- **Repair to overbroad test gating:** accepted English was being discarded as
  a native prerequisite merely because a separate Spanish generation held.
  Budget now retains only checked-language/result hashes (no raw prose) from
  actual immutable accepted results. A Spanish semantic hold still blocks
  Spanish; it does not erase independently accepted English. Unknown usage/
  closure remains a whole-package stop. Focused ledger boundary proof checks
  EN admission, ES rejection and in-flight global stop. Old four-trial package
  remains closed. No change to sources, thresholds,120limit or spending ceilings.
- **Prepared next planned stage:** distinct staged native runner uses the
  existing provider pre-dispatch counter for every HTTP/ASR/Live/native attempt,
  exact same hash-verified EN pair, optional independently checked input captions,
 45soperation/15sclose/11attempts/0.10reservation. No mic/player. Existing old
  launcher is unchanged and exhausted. Execute only planned English purpose;
  Spanish stays paused. Later repair/recovery slots retain their conditions.
- **Benchmark:** parent inspected Daniel's public3minute video transcript and
  metadata, not audiovisual timing. It is the historical two-turn quarter-cent
  example and describes multilingual/Pi as future work. Adopt continuous real
  interaction as the proof standard; no inferred latency/visual quality or new
  spend/source scope from that reference. Current fixed public redistricting
  trial remains engineering verification, not a complete showcase recording.
