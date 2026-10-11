# Decisions triage, view routing and UI component sources

Added October 11, 2026. Everything here is opt-in and off by default. It has been run offline only: no real Decisions request has exercised the `choice` or `score` question types from this code.

## Decisions before Strands

`open_oracle/triage.py` sends one typed Decisions request per visitor question before any agent model call.

| Question | Type | Used for |
| --- | --- | --- |
| `intent` | choice of 10 | Category: measure wording, candidate statements, roster, retention, logistics, voting advice, prediction, personal ballot, data use, off topic |
| `asks_vote_recommendation`, `asks_prediction_or_effect`, `asks_personal_eligibility`, `embedded_instructions`, `multiple_parts` | predicate | Guardrails and the multi-part notice |
| `view` | choice of 8 | Which registered component opens |

Order of work for a question:

1. The existing free regex guards run first. If one matches, no Decisions call is made.
2. Triage runs. If it fails, times out or returns anything malformed, the ordinary engine path runs unchanged.
3. Voting advice, logistics and personal-ballot questions at or above 0.8 are answered by the existing fixed responses from an exact-source engine. Embedded instructions and off-topic requests that name no contest get the existing "could not identify a contest" response. Strands and the output review are not called for these, which is where the saving is: one Decisions call instead of four to six agent calls plus a review.
4. Everything else goes to the engine as before. Afterwards the `view` choice replaces the view plan only if `validate_view_plan` accepts it for that already source-bound response. It never changes the answer text, the card or the evidence.

`DecisionsTriage.rank` scores passages with `score` questions and keeps the top three when a search returns more than three. `TriagedEngine` wraps the live selector so the agent's `search_evidence` tool sees the ranked list. Candidate comparisons are never trimmed. The current corpus rarely returns more than three passages for one contest, so this mostly matters for the larger research registry, which is not wired to it yet.

Triage is a router, not a release gate. It cannot release content or widen scope. The 0.8 threshold is uncalibrated. The response carries a `triage` object with categories, probabilities and token counts, never the visitor's words.

Enable with `--triage` alongside `--decisions` or `--live`. `/api/health` reports `input_triage`. The request cap from `--max-live-requests` does not count the triage call.

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
