# Claim evidence and two readability outputs

This additive offline suite tests actual retained COMBAT source contracts and the existing installed Strands `test_ballot_readability` tool. It constructs no model/provider and denies Python network connections. It has no release authority. Correct structured facts do not prove arbitrary prose: the suite deliberately tests that distinction. All expected labels are agent-authored provisional development labels. Validation and locked test sets are empty, no model judgments have run, and human comprehension has not been measured.

Run from the repository after core imports this patch and the original pipeline fixture:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. .venv/bin/python -B -m unittest discover -s tests -p 'test_claim_readability_followup.py' -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. .venv/bin/python -B evals/run_claim_readability.py --output /tmp/claim-readability-report.json
```

The runner's default style input is `fixtures/literacy_styles.json`, SHA256 `4344e1a2509ba6dea42ae43f1ffea527c15cc5ee3f075c8f12b9dec859f8c573`, shared with the separately frozen pipeline patch. `--styles` selects its isolated staging path during review. There is one source of candidate text. The four style names are user-requested controls, never inferred education levels, formula categories, or measured comprehension.

## Exact per-claim evidence

`claim_packs.build_pack` reads the current trusted Corpus, checks fingerprint/original bytes, and obtains a specific `fact_catalog` anchor. Each pack preserves claim ID, typed value/unit, exact quote/offset/text hash, original hash, full source context and complete passage. Date claims refer to the printed notice header in the full extraction, not fabricated offsets inside the COMBAT question. Context includes Jackson County, election date, issuer, source role, retrieved/snapshot dates and retained version. A sample does not establish every current-law consequence or personal eligibility.

`deterministic_check` rebuilds context and independently applies canonical `assess_claim`. Known slots with a different number/unit/date/jurisdiction are contradictory. Unknown slots, broken anchors, changed versions or borrowed sources are unsupported by this pack. Unsupported does not mean globally false. No generic word/number overlap can admit arbitrary prose. Canonical `validate_factual_display`, neutral-advice controls, full release and language/operation guards remain independent and mandatory.

`decisions_draft` only creates provider-native request data after the bounded typed guard succeeds. Its separate predicates ask about faithfulness to exact evidence and uncertainty/attribution for that single claim. Whole-answer checks remain required; per-claim checks must not silently omit an unsupported clause. The model input contains evidence, not provisional labels or data splits. No HTTP transport is constructed here.

## Separate readability outputs

`readability_outputs.run_fixture_matrix` calls the existing `build_readability_tool` eight times with public authored fixtures. It does not register another tool. `checked_result` recomputes the existing deterministic report before projecting two outputs:

- `formula`: the unchanged reproducible report, including method, language, original/scored bytes and hashes, normalization, counts, numeric estimates and limitations. Existing English method is `open-oracle-flesch-en-v1`, cmudict 1.1.1, four decimal places. FRE/FKGL have no pass/fail threshold or application grade bands. Supplied/uploaded provenance remains unverified. Exact corpus provenance must separately pass the existing source-bound diagnostic verifier.
- `clarity_review`: six individually named Decisions predicates: essential jargon, honest current-law context, YES/NO consequences, material conditions, meaning preservation, and clear evidence/limits. Missing review is unrun, refusal is refused, malformed/unavailable review is unavailable. Probabilities are fallible and uncalibrated, not textual explanations, human ratings or comprehension measurements. No rationale/quote is invented from a predicate probability.

There is no composite score. The shared fixture's earlier Spanish-specific experimental counting is not promoted: this adapter uses the existing tool, whose Spanish scores and counts are null/unsupported. English FKGL cannot score Spanish meaningfully. Any future Spanish implementation needs audited token/syllable counts and language/domain validation before production interpretation. Original text, explanation and speech remain separate bound artifacts.

The parser retains .95 for atomic criteria and rejects .94. Model identity, ordered echoed names, primitive types and finite probabilities are checked via the existing canonical parser. This is a diagnostic eval parser, not a runtime acceptance token. Every result explicitly says production release is unauthorized.

## Evidence and calibration protocol

The 33 contract cases cover supported rate/duration/jurisdiction/name/header date; altered signed values/units/date; wrong quote/offset/source/version/authority; truncated conditions; invented repeal, safety and personal eligibility; missing fund; injected instructions; neutral crime wording, YES/NO definitions and advice refusal; assistant advice. An intentionally false-accept stub reports .99 for every case, demonstrating that actual deterministic guards still hold their bounded failures. These passes are software-contract evidence, not model accuracy or calibrated .99 confidence.

Before any threshold revision, obtain independently adjudicated supported/unsupported labels with source packs and reasons. Include semantically equivalent supported paraphrases and legitimate evidence-gap/refusal answers to measure false refusals as well as false accepts. Split by source/claim family, language and style to avoid leakage; develop rubric on development only, freeze validation policy, then evaluate an untouched test set. Retain refusals/missing/malformed/timeout as separate outcomes, not zero probabilities. Report confusion counts, sample sizes, uncertainty and probability reliability by language/task. The included `confusion` function is bookkeeping only; no calibration conclusion follows from its tiny synthetic test. Do not lower .95 merely to pass a held answer.

## Tonight's bounded trial and MacBook evidence

This suite makes no provider requests. Managed Bedrock is optional/disabled under the frozen Decisions-only handoff; unavailable provider access does not block the custom application checks. Offline evaluation does not authorize live requests, AWS provisioning, exports or retries.

After material repairs and frozen hashes, core can reserve one corrected supported-answer HTTP trial with explicit maximum model/helper/reviewer calls, time/token bounds, no repeats and terminal counters. Require claim-level exact evidence plus unchanged deterministic source/numeric/condition checks and the existing full Decisions review. A hold ends the trial; no threshold lowering or unchanged retry. Separately measure false-refusal/false-accept controls within a newly reserved labeled review plan rather than claiming calibration from that single positive trial.

Then the device owner runs two deliberately initiated MacBook turns with its integrated microphone/webcam; Pi is outside the critical path. Keep keyboard/source inspection usable when media is denied. First turn asks the COMBAT rate/duration; follow-up asks what NO means without assuming a repeal consequence. Each accepted display, completed generated transcript, exact approved script, factual/Decisions acceptance and manual Play must belong to the current request/evidence/language/style operation. Preserve approved-versus-generated comparison privately while the trial is active; only scripted public fixture evidence may be written to eval files. Test Stop/Erase between completion and Play and a late prior-turn callback: no stale audio/display, no extra calls, no resumed old operation. Actual audible playback, microphone capture and cancellation on device remain unrun here.

Operational telemetry accepts only finite enum/counters and trusted config/source-version metadata. It must not include visitor/model/tool text, provider IDs, raw errors, private draft hashes or per-visitor evidence history. The offline report contains authored public examples only. Cloud export is unverified and unnecessary for this suite.

## Official contracts

The [Decisions guide](https://developers.openai.com/api/docs/guides/decisions) and [create reference](https://developers.openai.com/api/reference/resources/decisions/methods/create) define native text input, named predicates with probability, typed answers and explicit refusals. The independent source/release checks, .95 policy, evidence packs, styles and no-retry bounds are application choices, not SDK guarantees. The real installed Strands tool invocation and deterministic formula are separate from model inference. Use the tested installed 1.59.0 API and existing registered tool rather than inventing framework functionality. The Strands documentation URL was unavailable through this worker's web tool during the follow-up; installed SDK tests provide the compatibility evidence here.

## Bedrock primary and OpenAI secondary comparison

Daniel now directs Bedrock as primary Strands inference, with OpenAI for secondary reasoning. Decisions and GPT-Live retain personal OpenAI. Core owns controlled provider configuration, actual permission/model/region verification, bounded benchmark allocations and any default change. This eval package configures or invokes neither provider. `evals/provider_comparison_plan.json` specifies identical source-pinned compound cases, tools/schema/policy, source/numeric/condition/review gates, and cancel/token/time bounds for both profiles. Supported facts plus missing law or advice refusal must preserve separate part coverage.

Retain trusted configured provider/model/region, finite fallback reason, actual dispatch counts by role, tool/schema categories, observed usage or unknown, wall latency, reservation and measured estimate separately from invoice cost. A missing helper/fallback counter is unknown, not zero. Operational metadata remains content-free. Compare actual tool use, schema compliance and source faithfulness separately from whole-pipeline release. Synthetic traces or transport identity do not establish real provider execution, primary readiness, fallback success, improved quality or cost/latency savings. No default promotion follows before core's pinned live proof.
