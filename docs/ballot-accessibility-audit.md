# Local ballot accessibility audit

This is a separate preparation/audit workflow, not a voter-facing server route. It reuses the retained official source registry and the existing `test_ballot_readability` tool. It covers the six policy questions in the KCEB November 3, 2026 combined sample ballot, September 14 revision. Candidate evaluation and judicial-retention scoring are excluded. It does not determine an individual's ballot.

The runtime skill is bundled at `open_oracle/skills/ballot-accessibility-audit/SKILL.md`. It is adapted from Daniel's reusable ballot accessibility audit procedure. Computer History recordings, local memory paths and private provenance notes are not runtime resources.

## Run locally

From the project root, prepare all six questions and five separate fiscal summaries without model inference, credentials, downloads or network calls:

```sh
OTEL_SDK_DISABLED=true .venv/bin/python -m open_oracle.ballot_audit
```

The command saves a private JSON packet and readable Markdown report under ignored `.local/ballot-audit/`. It uses the existing retained research archive; the normal bootstrap/runbook explains archive preparation. Original PDF and extraction hashes must match the inspected version. Other ballots and authorities fail closed; this first adapter is deliberately scoped to the tested sample.

For actual local inference, explicitly select an already-installed, tool-capable Ollama model:

```sh
OTEL_SDK_DISABLED=true .venv/bin/python -m open_oracle.ballot_audit \
  --ollama-model qwen3.6:latest --timeout-seconds 180 \
  --output .local/ballot-audit/kceb-local.json
```

Use `--measure combat` to limit the audit to one question. No model is selected or downloaded automatically. The adapter uses the installed Strands OpenAI-compatible provider against fixed loopback `127.0.0.1:11434`, with an ignored placeholder key, zero transport retries and a 45-second per-call timeout. It rejects uninstalled models, cloud-named models, remote-backed model metadata and models without completion/tool capabilities. A between-call deadline and model/tool/context limits bound the agent loop; the deadline is not an interrupt of an in-flight provider call.

The native Strands `AgentSkills` plugin loads the bundled skill. An actual Agent resolves scope, reads exact ballot evidence, runs the registered readability tool, optionally searches and reads retained official legal context, and returns typed private explanation claims. Local inference runs sequential independent requests per question, each with its own deadline and budgets, then combines results with matching provenance. This avoids growing a single model context across the entire ballot. Metrics come from tool results, not model output. Recoverable tool errors are recorded; finalization still requires successful reads, scores and valid citations.

If a model draft fails, the batch discards its partial claims and independently reruns source checks and scoring through tools-only preparation for that question. The report labels this fallback, records the model attempt/error type, and adds `model_draft_unavailable`. `model_drafts_complete=false` and the execution label distinguish a mixed packet from completed model drafting. Original corruption still fails closed because fallback preparation repeats the original-hash checks. Cancellation propagates; it does not start fallback work. Tools-only preparation is also usable independently.

## Source and output boundaries

- Election, authority, measure set and source version belong to the application, not tool arguments. The existing registry checks authority, date, source roles, original hashes and exact parent spans. This integration also fills missing KCEB measures when another runtime feature supplies only a subset.
- Scoring requires a same-request original read. It calls the existing corpus-bound readability tool, preserving exact input, normalization records, counts, method version and provenance. Question and fiscal summary stay separate; COMBAT's trust-fund sentence stays with the question.
- Explanation citations must refer to read chunks of the same measure and pass the existing unique exact-quote and extraction-quality checks. As in the existing research agent, tools issue exact-span IDs so models need not reproduce PDF line breaks; the application resolves these IDs to the unchanged original and applies the same quote checks. Current law and adopted proposals remain distinct. The typed draft has a separate `missing_aspects` field for evidence gaps; factual claims still require citations. Missing aspects are independently derived from the final claims, regardless of the model's declaration. Duplicate or contradictory declarations fail validation. The retained registry currently provides more legal context for COMBAT than for the state measures.
- Exact citations establish provenance, not whether a generated explanation preserves meaning. Every packet keeps `public_display=false`, `speech=false`, and `release_state=private_awaiting_quality_review`. There is no release adapter or route to the public interface in this workflow.
- No current-source refresh, court-status reconciliation, PDF/keyboard/screen-reader certification or reader-comprehension testing is claimed. Readability is a surface diagnostic, never a fidelity or accessibility pass.
- The trace contains tool names and measure IDs, not model messages or claim text. The private review packet intentionally includes source passages and draft claims; it is not an operational receipt or public artifact.

## Validation and evaluation limits

Run the focused offline contract checks:

```sh
OTEL_SDK_DISABLED=true .venv/bin/python -m unittest discover -s tests -p test_ballot_audit.py -v
```

Tests use actual Strands skill activation, tools, structured output and retained official archives with **authored model events**, not live model inference. They verify all six scores and five fiscal units, required tool order, complete measure coverage, source/version scope, wrong-measure/unread/forged citations, retained-context retrieval, changed originals and cancellation. Assertions target observable boundary failures rather than stylistic similarity.

Observed risks from the sample audit determine this coverage: interleaved PDF columns, incomplete measure inventory, changed source versions, proposal/current-law confusion and missing conditional legal effects. No LLM judge is introduced. A separate Codex source-informed editorial review covers the six rerun explanations, with corrections and per-claim findings under ignored `.local/ballot-audit/kceb-reviewed-explanations.md` and its JSON companion. This review does not change runtime claims, supply human-labeled evaluation, test reader comprehension or validate the public release adapter. Actual passes, skips and local-model limits are recorded in the [implementation validation note](ballot-accessibility-audit-validation-2026-10-11.md).

Version-compatible references: [Strands native skills](https://strandsagents.com/docs/api/python/strands.vended_plugins.skills.agent_skills/index.md), [Ollama OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility). Implementation was checked against installed Strands 1.59.0, without a dependency upgrade. The documented `reasoning_effort=none` control keeps the local compatibility request from spending its output budget on a thinking trace; an unsupported extra `think` field did not do that in the initial probe.
