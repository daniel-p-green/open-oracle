# Optional Decisions triage: bounded advisory candidate

This is a staged triage-only change, not enabled runtime behavior or measured optimization. Core owns import/Git, request reservation, source/release, privacy and telemetry integration. The baseline triage files were copied read-only from `6ce8d169f9305f2ff76350d3b9dc6671cf318929`; their SHA256 values are in the handoff manifest. No paid calls, shared edits, credentials, deployment or Claude call occurred.

## Verified native contract

The [official Decisions guide](https://developers.openai.com/api/docs/guides/decisions) and [create reference](https://developers.openai.com/api/reference/resources/decisions/methods/create) describe text input, `gpt-6-luna`, ordered named answers, per-question refusal, typed choice values/distributions/confidence, and score levels as objects with `label` and optional `description`. Scores are fractional expected ordinal indices. They do not produce arbitrary explanations or tool arguments; confidence is not calibrated factual truth. Installed OpenAI Python **3.28.0** exposes that contract. An actual SDK request/response passed an in-memory MockTransport with sockets forbidden. This verifies local serialization/parsing, not API access or model performance. No files/images/audio are sent in this lane.

The original scorer's four string levels are invalid for the native schema. The staged `ranking_questions` draft changes them to four `{label: ...}` objects with the same labels/order. Ranking inference stays disabled; this helper is an offline contract/export seam.

## Change ledger and before/after

| Change | Kind and hypothesis | Preserved boundary |
|---|---|---|
| String score levels → `{label}` objects | Schema repair only | Same four labels and ordinal order; no scorer executes |
| Strict model/names/types/finite values and uncertainty validation | Adapter repair | Refusal distinct from zero; typed Boolean/string values; missing usage unknown; no invented confidence formula |
| Existing category definitions moved into option descriptions | Wording/layout candidate | Existing machine values retained |
| Explicit `other` for mixed/ambiguous/outside taxonomy | Separately identified taxonomy change | Does not mean verified off-topic; full engine fallback |
| Remove canonical request substitution, fixed-engine release shortcut and top-three ranking | Workflow/policy repair | Full original, scope, contest/candidate identity and every evidence candidate survive; mandatory release is unchanged |
| Skip optional classifier for known/invalid/scope/multi-part requests | Deterministic optimization candidate | Existing guarded engine still answers original request; no claimed planner reduction |
| Focus only accepted full-facet plan without uncertainty or multi-part flags | Conservative view policy | No generic measure facet invention, partial-answer hiding, text/evidence/review/speech mutation |

Original choice instruction: choose a single best category with values alone; original routing then substituted “Where is my polling place?” for a winning logistics category. Proposed choice uses descriptive option records plus explicit `other`. The application always sends the complete original to the existing guarded engine; the choice is advice. Independent intent/view/guard questions share one text input, with no sibling-answer dependency. `native-request-drafts.json` in the isolated handoff contains before, schema-only repaired score, and separate advisory candidate request bodies; none were executed remotely. Prompt/taxonomy and workflow changes are not presented as a schema-only equivalent baseline.

## Runtime behavior and reasons

1. Existing server/session guards reserve the request and check cancellation. The triage module does not reserve another request or retry.
2. Exact known questions/guards, historical/wrong authority/missing scope, source-integrity problems and obvious multi-part requests skip classification. A focused public ambiguous request can make one bundled call. No repeated ranking or selector mutation occurs.
3. Invalid/missing/refused classification falls back to the original full guarded engine. This is not an authorization to bypass a provider safety refusal; no private draft is used or released. Cancellation propagates and does not start a fallback call.
4. Classifier guards are explicitly **advisory**. They never replace release checks, establish eligibility, choose source identity/date, or authorize content. The existing deterministic and independent review still decides the answer. High confidence does not prove completeness or factual support.
5. Only a completed, validated full five-facet measure plan can change focus. Current implementation binds those facets to the checked COMBAT card; other measures remain source-only. Explicit parts, mixed requests, candidate sections, a rejected review, low confidence/distribution, or an invalid plan preserve the original plan. Touch/keyboard navigation is unchanged.

`routing_fallback_reason` is finite: `not_needed`, `classification_unavailable`, `multipart_preserved`, `guard_advisory`, `other_intent`, `low_confidence`, `accepted_plan_preserved`, `none`. Full precision drives the advisory focus; .799999 cannot round into .8. The inherited .8 threshold is uncalibrated and only controls view advice. Output Decisions .95 and source/numeric/scope/freshness/schema requirements remain unchanged. `multiple_parts` is Boolean; `advisory_guardrail_reasons` contains only registered predicate names, not provider prose.

Internal errors map to fixed `refused`, `malformed`, `timeout`, `transport_error`, `cancelled`. The observability follow-on mapping is respectively `classification_refused`, `response_shape_error`, `timeout_or_budget`, `transport_error`, `cancelled`. Malformed category intentionally combines name/choice/numeric/model failures; finer classifications require a reviewed finite projector. No arbitrary exception class, error message, provider ID, raw input, payload, evidence content or visitor hash enters metadata. Numerical choice distributions are projected by allowed typed values, stripping arbitrary extra keys. `policy_sha256` hashes trusted questions/model/policy only, not visitor content or source history. The deployment code hash must independently cover `triage.py`.

## Fail-closed release categories: required core boundary

Daniel explicitly approved task-oriented questions and separately dated source roles, with “better to be clear that we can't answer that type of question than mislead or be wrong.” This patch cannot widen the underlying engine's narrow released types. Core must retain explicit, distinct dispositions:

| Disposition | Meaning and user-facing example |
|---|---|
| `unsupported_question_type` | The app cannot support that kind of request: “I can explain the wording, but I can't recommend how to vote.” Forecasts/eligibility require their own explicit boundary. |
| `insufficient_evidence` | Eligible evidence for the requested part is missing: “I don't have a verified fiscal note to answer the cost question.” Silence is not proof of zero cost. |
| `conflicting_sources` | Eligible sources or versions disagree: “These source versions conflict; I can't give a checked explanation yet.” No automatic newest-wins rule. |
| `election_mismatch` / `jurisdiction_mismatch` | Wrong edition/date/board/district: ask focused context; never infer eligibility or silently replace sources. |
| `service_failure` | Retrieval/review/provider temporarily unavailable: “I couldn't complete the checks.” Distinct from an unsupported subject or missing source. |
| `release_held` | Deterministic, independent, schema or source check failed: no explanatory draft/audio; separately valid original may remain. |

These are a core integration contract, not new triage-created result statuses. A classifier failure alone is not a final answer failure when the full engine succeeds; confidence alone cannot set any disposition. In particular, the advisory module does not repair every preexisting unsupported-intent detection gap: core must prove a semantic recommendation/forecast request produces the correct refusal/gap rather than an `answered` card that does not address it. Default-off remains appropriate until this is reviewed.

For separable multi-part requests, every supported part requires its own eligible read and checked claim; every unsupported/missing/conflicting part receives an explicit gap. If separation is ambiguous, clarify or hold the whole explanation. An always-refuse policy is not a measured accuracy win; a short answer omitting the hard part is not successful coverage.

Ballot wording, current law, proposed changes, fiscal notes and court decisions are independent evidence roles with authority/election/date/version/hash/offset/eligibility. Candidate statements remain attributed. Similarity, a model score or an uploaded filename cannot promote a source. Raw uploaded/retrieved instructions remain untrusted. Substantive Strands reads and the same dated sources must support downstream Decisions review. No shared source-role registry/release expansion is implemented by this triage lane.

## Owner integration gates before enabling

- Keep `--triage` off until payload availability, full-request coverage/disposition policy, privacy disclosure, accounting and runtime fences are verified.
- Both `/api/ask` and `/api/ag-ui` reserve `max_live_requests` before `engine.answer`. It caps HTTP evidence requests, not provider calls. The new module adds ≤1 classifier per eligible request; the existing Strands/release cap still needs aggregate request-owned component accounting. No duplicate reservation or retry here.
- Inject the optional trusted `observer` into `DecisionsTriage` from the existing owner monitor. A `started` event has `attempt_delta=1`; terminal classified/unavailable/cancelled event has delta0 and known usage or explicit unknown. Sum deltas, not repeated event totals. Cancellation after dispatch must still count. Observer failures cannot retry or change release; if metrics cannot confirm a dispatch, keep accounting incomplete rather than claim zero. Default observer is absent.
- Optional-classifier metadata currently uses `unverified_provider` for the real transport, `offline_stub` for authored transports. Neither proves actual live inference. Promoting execution labels requires a reviewed live-proof contract.
- Add triage policy/code/schema versioning to the old operational receipt config and independently sanitize observer fields. Current outer deployment hash scans Python files and covers triage, but older EvidenceReceipt config omitted it. Do not hash visitor content or expose source history in aggregates.
- Update product data-use FAQ for the classifier's extra question/scope processing. `/api/ask` already intercepts narrow privacy/erase phrases; `/api/ag-ui` does not. The module raises fixed `LocalCommandRequired` on recognized local commands and makes no provider call; core must route that to the actual local FAQ/erase handler on both surfaces, not a generic 500 or a fake erased response. New exact “What does this guide record or send?” recognition must share this handler. Triage cannot erase a session by itself.
- Stop/Erase/session operation remains authoritative. Every late result/view must be rejected. The current synchronous HTTP transport can finish work already dispatched; cancellation cannot unsend it.
- Recheck finite view validity in AG-UI/speech display release. No frontend generated schema or new component is introduced.

## Evidence and limitations

The isolated module passes **33 authored triage tests**. The combined non-HTTP suite passes **62 checks**: staged triage plus canonical card/deterministic release, non-HTTP review/session/AG-UI checks. Five existing HTTP regressions failed to bind loopback in this sandbox (`PermissionError`); their log is retained and they are not reported as passing. No browser/audio/Pi or real model evaluation ran. Synthetic `real_api` labels in existing guard fixtures only exercise a branch.

The actual-SDK MockTransport test exercises POST serialization, native choice/score response objects, full typed distribution parsing and fractional scoring. Other controls cover model/name/type errors, missing/duplicate/extra options, NaN, low-confidence boundaries, per-question refusal, multipart tail preservation, wrong date/authority/contest, no selector/ranking mutation, canaries, current accepted plan integrity, rejected mandatory review, and cancellation before/during classification/engine work. These prove code behavior for authored cases; they do not measure routing accuracy, latency, source freshness or calibration.

Core must inspect the frozen manifest/hashes, check the patch against current files, run integrated HTTP/session/cap/privacy regressions with triage enabled and reviewed local handling, then separately decide whether the candidate is worth a live comparison. No live call is authorized by this document or the skill.
