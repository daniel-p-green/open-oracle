# Opus5.5High source review of664a4c4

Returned Message42 in the existing [OpenOracle review chat](https://claude.ai/chat/4c378210-7251-4026-9a90-700a23bc34d3).
Actual UI model/effort verified before submission: Opus5.5High. Source-only
bundle318924bytes/SHA256
5a66aba60d2f7a26e69bf9c656227746d0a9e6cde2cb8dcdaa51b7bded0942fc.
No credentials/account IDs/ledger/private voter or human data. Original returned
text and UI screenshot retained outside Git. Review was inspection, not execution.
Verdict: not ready.

| Finding | Disposition |
| --- | --- |
| S1 created delegation without completion falsely confirms spend | Fixed with creation tracking before cancel/drain and created-ID completeness requirement. Normal/canceled/drained creation-only regressions failed before and pass after. |
| S2 malformed nested decision escapes uncertainty | Fixed event/nested/decision type guards; decision:null regression failed before and passes after. |
| S3 absent completion should become zero-cost native_unused | Conservative hold retained. Official docs do not establish zero backend cost from absent native completion. No fabricated zero-cost event or manual reset; this can legitimately block progression. |
| S4 local pre-cancel transcription counts uncertain | Typed NotDispatched emitted before the provider counter/transport. Worker distinguishes proven local refusal from in-flight uncertainty. Other unknown errors remain held. |
| S5 internal accounting fence mislabeled user cancel | Layout propagates native usage uncertainty; Jobs keeps that internal reason/state held despite shared cancel. |
| L1 quiet mismatched tail waits deadline | Fail-sooner hold after2s quiet with mismatched transcript. A pause never authorizes speech completion/release. Short-tail regression passes; no measured live improvement yet. |
| L2 Missouri/Misuri spelling | Closed proper-name equivalence plus distinct-state negative control; native occurrence remains a hypothesis. |
| L3 Spanish turn retains English canvas | View uses response language for headings/map locale/source labels and locale-aware map reuse. English original/English legal snapshot remain labeled. Source/syntax verification only, actual browser render unverified. |
| Three-turn request bound | Separate bounded controls configured, old package unchanged. No execution is implied. |

Independent follow-up also bound conditional repair to the immediately preceding
held run/scenario and required an actual checked Spanish simpler transition
before a cancellation scenario can pass. Mock request-fit scores prove propagation,
not simplicity, factual quality or real language-choice accuracy. Provider/bilingual,
browser/accessible/human media and percentile latency acceptance remain open.

[Official graceful-close guidance](https://developers.openai.com/api/docs/guides/live-conversations#usage-and-graceful-close)
requires draining pending events and separate backend usage. Final voice seconds
alone are not proof of backend settlement.
