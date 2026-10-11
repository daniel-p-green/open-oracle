# Bounded evidence completion: isolated handoff

## Result and boundary

The staged `EvidenceCompletion` module supplies composable Strands tools and request-owned state, with no Agent/provider constructor and no network fetch. An actual Strands 1.59 authored-model run reads the retained JCEB ballot, exposes two missing facts, performs exactly one local approved-context expansion, reads the selected Ordinance 6096 spans, and returns a private structured evidence map. Twenty offline tests pass. This is SDK orchestration and provenance evidence, not live inference or semantic quality validation.

Every output has `public_display=false`, `speech=false`, `semantic_entailment_validated=false`, and awaits core source/quality review. No release contract, source loader, thresholds, shared code/Git or runtime was changed. Existing semantic encoders are never called by these context tools. No new provider call, resource, access change or upload occurred.

## Question and exact evidence map

> What does the COMBAT ballot ask to continue, what does Ordinance 6096 say about expiry, and what dates does its voter-approval condition specify?

| Required fact | Initial ballot coverage | Approved expansion witness | Claim boundary |
| --- | --- | --- | --- |
| `continuation` | JCEB ballot content chunk `combat:jceb-sample:8998:4a50da630896`, page 2, offsets 8998–9421 | None needed | The saved sample asks voters to continue COMBAT; no assertion of current law or voter approval. |
| `expiry` | Missing from the read ballot span | `combat:combat-6096-selected-v1:existing_expiry`, page 1, offsets 586–669 | Attribute the March 31, 2027 expiry and “unless continued by the voters” condition to the ordinance recital. |
| `conditional_dates` | Missing from the read ballot span | `combat:combat-6096-selected-v1:approval_condition_and_extension_dates`, page 3, offsets 2439–2717 | Attribute Section 4's majority-voter condition, April 1, 2027 effectiveness and March 31, 2037 automatic termination to the ordinance. |

Original ballot pin: `032814e650dbdbdb0064acb396ead6f51dcd087778240802eb6c30c7a5ef64a2`.
Ordinance original pin: `5fa4474560da047207bfd7c7033de0d0a1febb20d6e92cc6447982ca71a1afde`.
Selected reading pin: `229da53b66722072ed5f980c09ef91125b573fb1a18c333d2ed14961163f83a5`.
Full per-span hashes, source roles, offsets, page/section metadata and exact public quotations are in `evidence/source-map.json`.

The context route is explicitly `application_approved_context_not_printed_reference`: the ballot chunk does not print a link to Ordinance 6096. No invented citation edge is used. This is the trusted application's reviewed relationship between the ballot proposal and the ordinance, followed only after a per-fact gap. Both files are retained snapshots; there is no fresh-download or current-law claim. The ordinance remains `adopted_proposal`, partial verified reading copy, purpose `legal_reference`. Chapter 93 currency and Ordinance 4881 are not established by this slice.

## Mechanics and acceptance cases

The application supplies a fixed required-fact catalog and approved witness mappings for this narrow question. The model selects the order and tool calls, uses actual search/read results, sees explicit missing facts, chooses the approved route and composes a cited private explanation. `define_completion_plan` cannot omit a required fact. The host still owns free-text intake/decomposition; these authored fixtures do not prove general natural-language planning.

Local FTS searches are constrained to the approved source and purpose, then restricted to reviewed spans. Original, extraction, chunk, role, page, offsets, election, authority, county and server version pins are rechecked before read and at finalization. Structural controls and unverified OCR cannot become factual evidence. Citation IDs bind a fact and exact approved span; a read for one fact cannot authorize another. One expansion attempt is allowed, including missing context or failure. At most eight reads are allowed; the harness separately enforces eight model calls, eighteen tool calls, sequential dispatch, a between-call synthetic-token cap and no retry strategy. Production must retain core's existing lifecycle/hooks and provider call budgets.

Distinct failure paths:

- unsupported question type: an application-defined unsupported fact remains an explicit gap;
- insufficient evidence: missing context remains a gap; unverified source quality blocks source use;
- conflict: differing *reviewed mapping* keys for a fact prevent a factual finding;
- wrong election/jurisdiction: a held source boundary, distinct from stale/version integrity failure;
- temporary service failure: fixed metadata only, held output and no retry;
- cancellation/budget: blocks source work and delivery.

Conflict detection here is intentionally narrow: it detects disagreement among application-reviewed mappings that have been read. It does not infer contradictions across arbitrary prose, detect every conflict in an unread archive, or assert that the real expiry recital conflicts with conditional Section 4. A later semantic conflict checker must preserve both sources and remain subject to core review.

Tests cover source-byte/extraction injection before admission, explicitly approved but untrusted source text, fabricated/cross-fact citations, malicious claim text staying private, omitted parts, wrong scope, stale version pins, missing one/all context spans, mapping conflict, unverified OCR, unsupported prediction, request cancellation, provider failure/no retry, read cap, and a configured encoder that must not be invoked. The claim-injection case deliberately shows that citation binding does **not** approve meaning: malicious prose can be a private draft but cannot be released through this module.

## Narrow core integration proposal — not applied

Keep `research_agent.py`, `research_engine.py`, source/release logic and new `CitedAnswer` schema under core ownership. Import this new policy module only after reviewing the patch and baseline pins. Do not replace those files.

1. In an explicitly selected private completion lane, construct the policy using the **same fresh request registry, trusted Scope and `request.check`**. The host's intake must bind all requested parts to application-approved fact definitions, or return unsupported/clarification before invoking research. Do not turn arbitrary question text into trusted source pins.
2. Append the six policy tools to the existing request's tools, add only their fixed names to the existing allowlist/operational receipt enums, and append the completion instructions plus descriptor to application context. Retain core's `Controls`, `EvidenceReceipt`, sequential executor, schema collector, limits and cancellation. No second Agent/controller or additional inference pass is required by the policy.
3. **Required bridge before using existing `CitedAnswer`:** after a successful policy read, core must independently validate the corresponding planned part/purpose, source eligibility and exact citation, then register the chunk and issued raw span in its existing `read_by_part` / `citation_spans`. This module does not silently mutate those core structures. Suggested callback seam: `on_completion_read(fact_id, approved_span, issued_id, exact_citation)` after the policy's verification and before returning the tool result. Register only if the fact-to-part mapping and registry identity match. Source acquisition/search membership should also be recorded under the existing part, rather than bypassed.
4. The harness-only `EvidenceCompletionDraft` demonstrates structured dispatch. Production should consume core's existing `CitedAnswer` and invoke the policy's coverage/provenance validation through a narrow adapter. Core must separately approve any additional gap enums or closed mapping; do not mislabel arbitrary unsupported questions as predictions. Source-integrity failures cannot be converted into successful claims. Part coverage and explicit gaps must survive the adapter.
5. Current public research release accepts rate/duration and forecast refusal only. Therefore this context question must remain held until core explicitly adds a small reviewed source/release mapping. Proposed source descriptions above preserve attribution and every condition; they do not establish general legal advice. Only after deterministic source/numeric/display checks pass may unchanged Decisions review run. Decisions confidence cannot replace source fidelity, and the threshold stays 0.95.
6. Follow-up/UI reuse is limited to retained immutable evidence IDs plus server-owned scope/version context. Start a new active request and revalidate/reissue citations. The module does not persist visitor transcripts or grant durable old-session citation authority. Erase invalidates pending work through the host lifecycle.

## Reproduction and deliverables

Run the isolated tests with the existing Python/Strands environment:

```sh
OPEN_ORACLE_CORE=/Users/danielgreen/Documents/Codex/open-oracle PYTHONDONTWRITEBYTECODE=1 OTEL_SDK_DISABLED=true /Users/danielgreen/Documents/Codex/open-oracle/.venv/bin/python -m unittest discover -s evidence-completion/tests -p 'test_evidence_completion.py' -v
```

The frozen patch adds only `strands_quality/evidence_completion.py`, a new test file, a public three-span test fixture and this integration document. It contains no modifications to core-owned files. `evidence/checkpoint.json` records baseline hashes, patch/deliverable hashes, SDK version and the offline proof. No live request is implied or authorized by these results; any future provider trial needs a separately scoped/reserved test after integration readiness.
