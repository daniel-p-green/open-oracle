# Ballot audit local validation, October 11, 2026

The separate local audit workflow is implemented and tested. Nothing was deployed or pushed. No cloud inference, paid API, personal voter lookup, source refresh, voice or sensor operation was used. Existing unrelated working changes were preserved.

## Sample acceptance

The KCEB September 14 revision of the November 3, 2026 combined sample ballot was tested against original SHA256 `92cda731c864b5a84062322a32f743597bcace6f986af4c0e2bfe55c7405dc62`.

- Tools-only preparation covered all six policy questions and five separate fiscal summaries. All 11 normalized scoring text hashes, word/sentence/syllable counts and scores exactly matched the preceding rendered-page audit. No ballot average was produced.
- Actual local inference used installed `qwen3.6:latest` through Strands 1.59.0, with native skill activation and actual scoped source/readability tools. The final serial run made 43 model calls across six independent question requests. Five produced private drafts. Proposition A failed the structured-output contract after 13 calls; its partial claims were discarded and fresh hash-checked tools-only preparation retained its original wording, scores and explicit model-drafting gap.
- The final packet reports `execution=local_ollama_with_tools_only_fallback`, `model_drafts_complete=false`, `public_display=false`, `speech=false` and `release_state=private_awaiting_quality_review`. Every retained quote was checked as an exact unique source span. All six originals and all 11 complete scoring records matched the tools-only baseline.
- Outputs are ignored local review artifacts: `.local/ballot-audit/kceb-preparation.json`, its Markdown companion, and `.local/ballot-audit/kceb-local-all.json` with its Markdown companion. Full source passages and drafts remain local; none are committed as generated output.

## Regression checks

The following local suite completed 81 tests: **79 passed; two optional native AG-UI adapter checks skipped because the extra adapter is not installed**.

```sh
OTEL_SDK_DISABLED=true PYTHONPATH=.:tests .venv/bin/python -m unittest \
  test_ballot_audit test_readability test_readability_integration test_research \
  test_research_release test_research_clarity test_verified_passages test_strands
```

These tests use retained archives and authored model events through the actual SDK, without model inference or network calls. They verify required source reads and scoring, complete and unique measure coverage, source scope/version, exact citations and issued span IDs, context source roles, changed originals, cancellation, loopback provider configuration and explicit fallback. A corrupted original and cancellation cannot be hidden by fallback. Syntax and whitespace checks also passed.

## Observed failures and remaining limits

**Source coverage: fixed.** A runtime feature supplying only a subset of KCEB measures caused the registry's former empty-only fallback to omit other measures. The registry now fills missing hash-pinned KCEB measure spans while preserving existing entries and scope checks.

**Quote fidelity: fixed mechanically.** A local model normalized source line breaks when copying a quotation. Audit tools now issue exact-span IDs, following the existing research-agent pattern. The application resolves these IDs to the unchanged original, then applies the existing quote checks. Fabricated, unread and wrong-measure citations remain rejected.

**Provider reliability: limited.** The small installed Llama model failed structured output. Initial Qwen trials exposed the need for the documented reasoning control and smaller per-question contexts. Qwen still failed on Proposition A in the final run. The workflow handles this as an explicit drafting gap, not a successful model audit or automatic retry. Recoverable tool/schema errors are recorded and may be corrected before finalization.

**Semantic quality: unvalidated and private.** Exact citations do not prove entailment, legal fidelity or neutrality. The local drafts leave substantial baseline, YES/NO, conditions and terminology gaps, especially where the retained registry lacks state-measure legal context. No calibrated LLM judge, human-labeled civic-quality evaluation or reader study is available. Review all generated claims independently before any public use; the integration supplies no release path.

**Access/current status: not retested.** This implementation did not refresh official pages, resolve current court proceedings or perform keyboard, screen-reader, contrast or PDF conformance testing. The existing readability estimate remains a surface diagnostic, never a comprehension or accessibility pass.

## Follow-up: Proposition A fix and six-explanation review

The earlier acceptance record above is preserved as the failed baseline. A targeted local diagnostic reproduced Proposition A’s failure: the model submitted unsupported-aspect notes as factual claims with empty citation lists, received seven schema errors, repeated the invalid claims, and finally failed forced structured output after 13 calls. No quotes, source scopes or citation requirements were relaxed to accept that output.

The typed draft now gives missing evidence its own `missing_aspects` field, with explicit schema, prompt and runtime-skill guidance. Claims still require at least one citation. Duplicate or contradictory gap declarations fail validation, and the application continues deriving its own gaps from the final claims. An actual-SDK regression failed on the pre-fix schema because the new gap field was rejected and exhausted the bounded loop; it passes after the fix. A separate regression verifies that uncited missing-evidence placeholders still cannot pass as claims.

A targeted real-local Proposition A run completed in six model calls. The subsequent complete six-question run also succeeded: **36 actual local model calls, six private drafts, 27 generated claims, no tools-only fallback**. Per-question calls were 5/7/5/7/6/6 in ballot order. One recoverable structured-output validation error was recorded. The model remains `qwen3.6:latest`, Strands 1.59.0, fixed loopback transport; no dependency upgrade, cloud inference or paid API was used. All six original records and all 11 complete readability records exactly match the earlier tools-only baseline. The packet retains `public_display=false`, `speech=false`, and `private_awaiting_quality_review`.

Local outputs: `.local/ballot-audit/kceb-local-proposition-a-fixed.json`, `.local/ballot-audit/kceb-local-rerun.json` and their Markdown companions. The original failed/mixed run is unchanged. A separate `.local/ballot-audit/kceb-reviewed-explanations.md` and JSON companion record the source-informed editorial review of every one of the 27 claims, with six corrected explanations, official references, input hash and explicit source-access limits. The reviewed export is separate from the runtime release packet and leaves public display/speech disabled.

The source review corrected or qualified these observed semantic problems:

- Amendment 3: preserve medical, minor-consent and gender-treatment exceptions, and distinguish fiscal estimates from legal conditions.
- Amendment 6: the 80% vote in each chamber refers a proposed change to voters; it is not direct legislative enactment.
- Amendment 7: the appropriation restriction is conditional, earnings can be used under the stated approval process, the principal is protected, and withdrawal/fund-failure conditions matter.
- Amendment 8: sheriff elections already exist in statute; preserve covered-county exceptions, Attorney General initiation and court removal rather than unilateral executive removal.
- Proposition A: identify HB 1 and attribute the 2022-map NO effect to official fair-ballot language; avoid inferred design intent, party-benefit claims or a determination of today’s operative candidate map.
- COMBAT: add April 1, 2027–March 31, 2037 continuation dates, the March 31, 2027 expiration if not continued, the sales-tax basis and separate fund; distinguish enabling law from completed voter authorization.

Fresh downloads of HJR 73, SJR 95, SJR 87 and Ordinance 6096 matched the retained hashes. Current constitutional/statutory baseline sources and official COMBAT pages were read. A6’s scanned operative pages and COMBAT’s date provision were visually checked. SOS direct retrieval and A6 direct refresh failed; official indexed fair-ballot text and the retained A6 original were available. The official September 3 SC101805 opinion was found through search, but direct PDF access returned 403; no comprehensive later-court-order reconciliation or personal district determination is claimed. The review is Codex editorial work, not human legal approval, a calibrated semantic evaluation, reader testing or validation of the public release adapter.

The final focused offline suite completed **85 tests: 83 passed and two optional AG-UI adapter checks skipped**. It uses authored model events and retained sources; the real local model reruns are separate evidence. Whitespace and syntax checks passed. No public server, voice, deployment or publishing change is part of this follow-up.
