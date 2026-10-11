# CopilotKit controlled integration — actual local path

Open http://127.0.0.1:8765/copilot after starting the ordinary local server. The main / browser remains available. This optional page is a working controlled CopilotKit/AG-UI integration, not a new chosen visual direction.

## What runs

Installed pinned @copilotkit/react-core1.78.0 and @ag-ui/client1.0.2 from public npm, with install scripts/audit disabled. The page uses actual `CopilotKitCoreReact`, its React context, `useAgent` and `HttpAgent`. `copilotkit.runAgent` runs the transport; the hook observes accepted `STATE_SNAPSHOT` data and selects a typed measure or candidate component. This is not a custom card relabelled as a library integration. Local direct-agent registration uses the SDK's explicit development-only API; no production hosting or hosted Intelligence claim is made.

POST/api/ag-ui invokes the existing substantive EvidenceLoop/Strands selector when explicitly live-enabled. It does not start a second agent. It finishes deterministic source/display binding and any required Decisions checks before emitting buffered state and completed application-owned renderEvidenceView descriptors. The official useRenderTool/useRenderToolCall hooks validate strict component parameters and render the approved catalog. Raw provider prose, provider tool arguments/results, trace diagnostics, reasoning and draft UI never enter the stream. Bound original quotations remain available when explanations are withheld; they are labelled without claiming independent AI review. Rejected content receives a second withholding check. Default exact-source mode is clearly labelled independent-review-off.

The adapter accepts one current reviewed text question, bounded run/thread IDs and explicit application scope. It rejects frontend tools, context injection, resume payloads, forged assistant messages and invalid scope before work. Client state/history is not passed to the model. Reset invalidates request identity, aborts transport, clears state/messages and changes thread ID; stale response identity cannot render a card. No browser persistence or transcript telemetry was enabled.

## Open Intelligent UI relationship

The requested [Open Intelligent UI repository](https://github.com/CopilotKit/OpenIntelligentUI) combines CopilotKit/AG-UI with native components and a generated sandbox. This slice uses the genuine controlled CopilotKit layer, while preserving Strands and the evidence gate. It does **not** install the entire Next.js/DeepAgents reference app or enable its generated HTML/JavaScript sandbox. No TypeSafe visual-router account, additional model, CDN execution, iframe or hosted service was added. The remaining open-ended sandbox integration requires a separate design/safety decision; do not call it completed.

The first full provider bundle pulled Markdown syntax grammars, Mermaid, inspector and other unused UI into16.3MB. The documented headless/context entry reduces the current bundle to about1.4MB. Source, pinned lockfile and build config are in web/copilot-src; the runtime bundle is web/copilot.js. This remains additional frontend cost and has not been measured on the Pi.

## Actual checks

Isolated headless Chrome against a real ephemeral loopback server passed COMBAT, original wording, NO follow-up, unsupported prediction, reset,800×480/320px reflow, zero page errors and zero external requests. Current test mode is exact-source; no live provider, microphone, playback or generated sandbox was exercised. SDK/React TypeScript checking and bundle build pass. Offline tests cover source release, withheld claims, forged client input, identity, actual SSE and cross-origin rejection.

A live-gated browser success is still blocked by the observed Decisions quality-control failures. It cannot be claimed from this no-model browser check. Physical Pi, speech alignment, translations, and final design selection remain unverified.

References inspected: [CopilotKit Strands](https://docs.copilotkit.ai/strands/quickstart), [headless useAgent](https://docs.copilotkit.ai/reference/hooks/useAgent), [AG-UI HTTP agent](https://docs.ag-ui.com/sdk/js/client/http-agent). Actual installed exports/types were used to build this path; no outdated template assumptions were substituted.

Final combined check:50/50 Python tests,51/51 authored offline Promptfoo, both browser harnesses, strict orb/CopilotKit TypeScript, JavaScript syntax and offline Live lifecycle pass. Candidate roster and attributed source-pointer paths also passed. Canonical CopilotKit source/types/lockfile match the tested staging bytes. Rebuild from web/copilot-src with `npm ci --ignore-scripts --no-audit --no-fund` followed by `npm run build`; the script writes the sibling web/copilot.js. The built bundle is already present, so normal server startup requires no Node install.

Current deterministic/adaptive checkpoint:71/71 Python tests and51/51 authored offline Promptfoo, strict schema-renderer TypeScript/build, both browser regressions and poisoned-facet fallback fixtures pass. See [current release contracts and limits](deterministic-release-2026-10-10.md). No paid calls or freeform sandbox were added.
