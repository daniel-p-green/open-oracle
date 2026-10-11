# Deterministic evidence release and constrained adaptive UI

The local app now supplies a useful sourced path independently of the fallible Decisions scores. Default mode remains a dated exact-source browser with fixed COMBAT explanation contracts and full attributed candidate answers. A failed explanation or live retrieval now exposes **verified original wording** with an explicit “explanation withheld” label. It does not relabel that quotation as an independently checked AI answer.

Try either `/` or `/copilot` on the existing loopback server:

- “Explain COMBAT” — navigate its five approved source-bound parts.
- “What is the COMBAT rate?” — focus the rate and its exact source wording.
- “How long does COMBAT last?” — focus duration.
- “I still don't understand COMBAT” — return to one part at a time.
- “Compare Pollard and Fields priorities” — show both complete attributed answers to the same question.
- Browse the 55 retained contests; other positions, legal effects and current personal eligibility remain explicit gaps.

## Facts do not inherit a classifier probability

`claim_bindings.py` enforces a finite factual contract. The COMBAT rate, duration, county and name bind to exact offsets/quotes in the retrieved passage. The election date binds to the printed header in the checksum-verified retained document reading copy, with a distinct `printed_document_header` reference; it is not assigned imaginary offsets inside the question. Printed candidate-name spans are bound where available. Candidate-speaker attribution is separately verified against the pinned prepared-source identity and complete quote hash.

Typed values use bounded decimal/fraction normalization, entity normalization, and ISO-date validation. Every anchor includes evidence identity, original-document SHA, reading-text SHA, start/end offsets and the exact original quotation, including its line breaks. Corpus and contest fingerprints are captured at load; mutating a shared in-memory source object cannot rebind its original identity. Quoted claims must exactly match their retained passages.

- **Supported:** a registered typed fact and its exact source anchor agree.
- **Contradictory:** a known fact slot disagrees, such as 5 percent instead of the printed quarter-cent rate, twenty instead of ten years, another county, or another election date.
- **Unsupported:** no contract establishes the claim, or a type/source-span binding fails. A prediction of 50 percent crime reduction is unsupported, not a contradictory tax rate merely because it contains a percentage.

Matching words or numbers never proves an arbitrary sentence. Explanation prose must match the finite approved display contract; a same-number negation, personal-ballot assignment, altered title/facet, detached claim quote, or unknown widget is withheld. This is **not general English entailment**, and it makes no calibrated correctness claim. New paraphrases/facts need additional audited source contracts. No tax-unit conversion beyond the explicit quarter-cent contract is inferred.

Focused rate/duration/fund/purpose API answers use the same approved facet text as the visible component. The printed rate is now stated directly as one-quarter of one cent; the exact quotation remains visible. This does not establish audible speech alignment.

The deterministic gate precedes any Decisions call. A judge accepting an unsupported fact cannot release it. The AG-UI boundary rechecks substantive display bindings against the actual corpus before streaming. Decisions remains an optional-in-exact-mode / required-in-live-mode, fallible additional explanation gate; clarity probability is not factual correctness. Its previously observed failures and frozen comparison remain preserved, with the threshold unchanged at 0.95.

## A useful original-wording fallback

The fallback contains only retained source records, attribution, scope and their mechanical fingerprints. It excludes the rejected answer, card and derived claims. It is bound to the current request/contest and checked again before AG-UI delivery. Scope/date conflicts and absent or corrupt evidence cannot create it. A failed live selector can retrieve scoped local originals without making a further quality API call. Candidate quotations still carry the notice that their statements are not independently verified outcomes. Speech remains held; this fallback is not forwarded as validated generated audio.

## Actual constrained component path

The `/copilot` route now uses the official `useRenderTool` and `useRenderToolCall` hooks with a strict Zod schema, in addition to the existing `CopilotKitCoreReact`, `useAgent` and AG-UI `HttpAgent`. The app emits a completed `renderEvidenceView` descriptor **after** source/display validation. It is application-selected from the request, not claimed as a newly proved model-generated UI plan.

The catalog contains `measure_parts`, `measure_focus`, `candidate_quotes` and `source_quotes`. Parameters contain only component, request/source IDs, approved facet keys, initial-part index and English language. Extra properties, foreign sources, stale requests, arbitrary components, HTML, scripts, styles and new display prose are rejected. The renderer displays only complete parameters matching the released snapshot. Navigation can select only the already checked facet set; it cannot introduce a later generated fact or expression. All factual strings come from approved contracts or mechanically bound original text.

This follows the native component/schema alternative documented in the pinned [OpenIntelligentUI generative-UI guide](https://github.com/CopilotKit/OpenIntelligentUI/blob/f6e4388b26a64b9a0714943b08a1ce622b924eec/docs/generative-ui.md). Installed official exports and types were inspected and strict TypeScript passed. There is no new agent, model, hosted runtime or frontend execution tool. Incoming client tools/state/context remain untrusted and rejected/ignored. The whole release is buffered; raw provider tool messages and reasoning are never streamed. Only the application-owned validated display descriptor uses the tool-event rail.

This is a working **constrained adaptive catalog**, not full freeform OpenIntelligentUI. Its HTML/JavaScript sandbox and later expressions remain disabled because the actual sandbox test demonstrated replacement of reviewed text. Richer catalog components and model-selected layout can be added behind the same contracts; neither is claimed tested now.

## Verification and remaining blockers

- **71/71 Python tests**, including actual Strands SDK offline orchestration, source/claim tampering, numeric/entity/date conflicts, unsupported predictions, alias mutation, rejected explanations, local retrieval fallback, scope limits and schema injection.
- **51/51 authored offline Promptfoo cases**; no inference or AI judge used.
- Strict CopilotKit TypeScript and the production bundle build pass. Zod 4.6.5 is pinned directly in the matching package/lock files.
- Both browser regressions pass. A separate actual headless browser fixture exercised rate/duration/step adaptation through the official CopilotKit hooks, then injected a bad 5-percent facet: both routes withheld it and showed the bound original. Zero page errors, external requests, iframes, model calls or capture. Screenshots and JSON are in task `deterministic-release/`.

No paid calls were made for this work. Conservative reservations remain **$3.95 of $5**, leaving $1.05 unallocated. The prior 64-request Decisions comparison is preserved and was not rerun or tuned using held-out results. Existing Opus diagnosis informed quote and translation boundaries; no new Opus call was needed.

Fully validated live explanation/speech, audible Mac playback, speech/display alignment and reviewed translations remain unproved. Mechanical source fallback works even when live explanation is unavailable. Pi microphone capture remains absent per the hardware handoff; HDMI playback, real Lumina capture and physical Pi frontend validation are unverified. The default app remains **127.0.0.1:8765**, with no Pi-reachable LAN/HTTPS URL or network/security changes. Research, memories and credentials were not modified; no publication, deployment or submission occurred.

Final running-server smoke: actual loopback HTTP returned supported rate, duration and full attributed Pollard–Fields comparison in exact-source mode. Server session5026; voice not connected and playback held. No command or test is stalled. See evals/deterministic-release-20261010/final-checkpoint.json.
