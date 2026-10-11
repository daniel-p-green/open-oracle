# Nonvisual readability and operational receipts integration

No web file, orb, input bridge, voice transport, release threshold, source original or visual concept changes.

## Readability

`EvidenceLoop.answer` recognizes explicit readability/Flesch/FKGL/reading-grade/reading-level requests. Current HTTP `/api/ask` and CLI callers receive `readability` metadata, which is a diagnostic alongside the existing supported response. There is no new grade renderer and no score is inserted into speech.

Exact-source mode calls the actual Strands-decorated deterministic tool directly, with zero model inference. Agent mode registers a narrow `test_ballot_readability(evidence_id)` schema only for these measure requests. It requires an already-read passage from the resolved contest; the app injects language, question/fiscal span and jurisdiction. Selected IDs must have a completed scoring report. The default three-tool workflow is unchanged, and the existing five-model-call/eight-tool/25-second bounds remain. The new flow is resolve -> search -> read -> readability -> structured selection; actual live success is untested.

Each report preserves complete original wording, source IDs/hashes and selected offsets. COMBAT's separate trust-fund condition remains in the complete question. Current app source IDs remain JCEB; independently verified KCEB fixtures stay separate. FRE/FKGL are formula estimates using pinned cmudict1.1.1, not exact Ballotpedia scores, comprehension, legal-effect, political-bias or factual-fidelity approval. Missing fiscal text is reported explicitly. No rewrite or ranking optimization is connected.

## Receipts and local evaluation support

Task-8's independent `strands_quality/receipts.py`, `local_metrics.py`, and `experiments.py` are incorporated. The final reviewed and locally repaired research modules are imported separately into the private service described below; the native adapter remains optional. The receipt's tool-name allowlist adds only test_ballot_readability.

One request-owned receipt runs as real Strands SDK hooks when an Agent is used. Finalization occurs in the outer application finally after source/display checks and independent review, including errors/cancellation. The response contains an operational_receipt; the loop holds content-free operation/error/latency counters. This is not a new quality gate or a factual-certainty claim. Aggregate token usage is observed in one slot rather than summed from the repeated legacy trace fields. If a provider fails before a final SDK result, aggregate usage may be unavailable; it is not recorded as zero spend.

Configuration fingerprints version actual implementation/policy files, trusted public source versions, SDK, configured model/reviewer identity, caps and retries. Agent requests additionally bind actual registered tool schemas, system prompt hash and output schema. Questions, visitor scope, request IDs and tool contents are excluded. Individual receipts have generated pseudonymous UUIDs and released source IDs; these are returned to that request, not exported or persisted as an event log. Aggregate counters omit all identifiers and source history. DebugReceiptBuffer exists as a library utility but is not enabled or instantiated by core; no new debug sink, telemetry exporter, feedback collector, retention guarantee or training flow is added.

Frozen configuration/case manifests, single-use heldout consumption, sanitized evaluation reports, explicit unknown qualities, human/live-evidence promotion recommendations and local rollback utilities are available independently. No current live run, calibration, automatic promotion or new heldout reliability claim is made. Existing task-8 historical fixtures remain consumed regression data. Concurrent registry writers still require locking before using that optional local utility.

## Audible proof handoff

The earlier real typed-to-playable buffer was erased and its browser closed. No reusable accepted media buffer remains. A fresh bounded generation is required, within the existing $50 testing authorization, coordinated with the foreground UI owner.

Once Daniel is present and the owner enables one capped live WebSocket trial on the existing loopback app: type `What is the COMBAT tax rate?`, submit Show evidence, select Prepare spoken answer, wait for Play answer, then Daniel explicitly clicks Play answer. Confirm the heard complete sentence matches the displayed accepted sentence, then Erase this session. No microphone or camera is needed for this typed audible proof. Never play automatically, start ambient capture, retry a paid trial silently or broaden LAN exposure. Main exact-source mode remains safe until that coordinated switch.

## Final reviewed research import

The final task-8 research modules and 14 review regressions were checked after the independent Claude Opus5.5 high static review. Staging fixes address the three P1 defects (date-purpose bypass, cut-through numeric quotations, fabricated partial legal references) plus related scope/pin/gap/lifecycle issues. The fixes were locally tested; Claude did not re-review them. This is not Claude approval or a production/legal-completeness claim.

`open_oracle.research.research_private` is an explicit model-injected private service. It requires KCEB or JCEB, enforces bounded requests, and returns only awaiting_quality_review drafts with public_display=False and speech=False. The normal browser/HTTP/evidence/voice paths are unchanged. Four hash-pinned archives and 99 filtered FTS5 chunks support model-planned question parts and exact citations; no live embedding, fresh HTTP or current Chapter93 completeness claim is made. Independent claim entailment, full question coverage, legal/neutrality and release adaptation remain necessary before connecting these drafts to public display or speech.

Native AG-UI remains optional and uninstalled in the active venv. Four native-only tests skip in the default suite; the complete adapter suite runs with the owner's isolated pinned extras. The dependency-injected direct Strands research route uses the existing installed SDK. A bounded public-source live trial needs its reservation coordinated in the shared $50 ledger before execution. No new live research calls or reservation are claimed in this integration.

## Slow venue internet

The existing served interface uses local scripts, styles, system fonts and a local orb texture; headless acceptance observes zero runtime external requests in the typed exact-source flow. Retained versioned originals are served locally with source SHA checks. Remote publisher links are explicit user actions. Typed exact-source evidence remains the working fallback when cloud services are unavailable; cloud voice and independent model review do not work offline.

Existing 40-second browser question timeout, abort/erase epochs, server request quotas, provider timeouts/no automatic retries, and SDK cancellation remain intact. Existing delayed-response browser and HTTP erase tests verify that stale results do not appear. No duplicate paid retry loop or network/security changes were introduced. Record the first video export around 5–6am Central on October11, leaving verification and upload time before the 8am deadline.
