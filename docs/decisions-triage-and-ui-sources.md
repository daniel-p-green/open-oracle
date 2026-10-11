# Decisions triage, view routing and UI component sources

## Optional Decisions triage — advisory revision

The triage-only proposed revision is documented in [decisions-triage-advisory.md](decisions-triage-advisory.md). It remains opt-in/default-off; no live classifier verification or performance result exists. The full original request/scope/contest goes to the existing guarded engine. Known guards/intents and multi-part or unresolved scopes skip the optional call. At most one classifier runs for a scoped ambiguous request; passage ranking is disabled and selectors are not mutated. Classification cannot approve or release an answer. Refusal/malformed/timeout means ordinary guarded-engine fallback, with no retries; cancellation propagates without fallback.

A completed accepted full-facet plan may be focused through the existing validator, only without multi-part or guard/uncertainty flags. Generic measures, candidates and limited-part responses retain their existing plan. Choice distributions/confidence are strictly parsed and sanitized; native score draft levels are label objects. Score inference is not enabled. Runtime facts, attempt/token accounting, session fencing and trusted configuration fingerprints remain core-owned integration gates. Existing `--max-live-requests` reserves HTTP evidence requests before the engine; it is not a per-provider-call budget.

This revision supersedes the old canonical-question replacement and top-three rank design. The historical offline UI/component checks below do not validate this new triage revision.

## Generative UI: what comes from OpenIntelligentUI

[OpenIntelligentUI](https://github.com/CopilotKit/OpenIntelligentUI) (MIT) is a Next.js, CopilotKit v2 and LangGraph reference app, not a component library. It has three tiers: plain text, native typed components, and `generateSandboxedUi`, where the model writes HTML, CSS and JavaScript into an iframe. A separate router picks the presentation for each turn with a typed `choice` question.

Adopted: tiers one and two and the router. The Decisions `view` choice is the router, and the existing CopilotKit `useRenderTool` catalog on `/copilot` plus the same view plan on `/` are the typed components.

Not adopted: the sandbox tier. Model-written markup cannot pass the claim, source and neutrality release checks, so it stays off.

## Voice UI: what comes from ElevenLabs UI

All from `github.com/elevenlabs/ui` (MIT) at the commit named in each file header, bundled into `web/orb.js` from `web/orb-src/`.

| Component | Use | Local change |
| --- | --- | --- |
| Orb | Presence and state | Same-origin noise texture |
| LiveWaveform | Microphone level while listening | Takes the stream the app already opened. It never calls `getUserMedia` and never stops tracks |
| ShimmeringText | The app's own status text while it works | Tailwind classes replaced by `.oo-shimmer` in `orb.css` |

Left out on purpose: TranscriptViewer needs character alignment timestamps, which GPT-Live does not provide and which must not be invented. AudioPlayer would sit beside the manual Play and receipt gate in `live.js`. Conversation and Message conflict with one card at a time.

Reduced motion turns off the shimmer and waveform; the plain status text stays.

The island also adds one line under the answer heading saying how the question was sorted. Its wording comes from fixed lists keyed by the triage category.

## Checked and not checked

Checked: 12 offline unit tests in `tests/test_triage.py`; the existing offline browser acceptance on `/` and `/copilot`; a browser run against an authored stub server on port 8767 showing the routing line, the fixed voting-advice response, the shimmer, and the waveform drawing from a synthetic test tone and leaving its tracks running.

Not checked: any real Decisions triage call, a real microphone through GPT-Live, and the Pi.

Rebuild after editing `web/orb-src/`: `cd web/orb-src && npm install --ignore-scripts && npm run build`.
