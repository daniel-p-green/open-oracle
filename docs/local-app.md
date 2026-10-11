# Open Oracle local application

October 10 update: [the two-path guide](two-paths.md) supersedes the candidate-position and AWS live-test gaps below for the bounded Pollard–Fields priorities/property-assessment slice. Both demo paths now passed real Strands + Bedrock smoke tests. Other gaps below remain unless separately verified.

This first complete text evidence loop covers the retained November 3, 2026 Jackson County inventory: 55 contests, 62 printed nominees, 11 retention questions and 10 measures. It does not assign a personal ballot. Candidate positions and judicial performance evidence remain explicit gaps in this slice. The retained samples are snapshots, not a newly certified current ballot.

## Run locally

From the existing project directory:

```sh
.venv/bin/python -m open_oracle
```

Open http://127.0.0.1:8765. Default mode makes no model/API calls, captures no microphone or camera, releases server-held exact source spans with provenance, and labels independent quality review as not run. No visitor question, address or audio is persisted. Retained ballot originals and 15 retained 2026 judicial-survey originals are served through allowlisted PDF routes; hashes are checked on the bytes actually served.

## Architecture and decisions

The browser submits question/context/request identity. `EvidenceLoop` resolves ambiguities, applies date/authority/locality constraints and handles neutrality, logistics and missing-source boundaries. `Corpus` indexes 55 exact reading-copy passages and checks the two PDFs, both reading copies and inventory against the inspected snapshot. Search and read enforce the same scope. Historical research is never indexed as the current ballot. Original wording and limitations remain visible together.

Explicit live mode uses a real Strands Agent and three substantive tools: resolve_contest, search_evidence, read_evidence. Application-owned scope cannot be rewritten by a tool argument; selected IDs must have been read in that request. Provider prose is not released. Model calls/tool calls have budgets, provider timeouts and no retries. Default local retrieval supports progress while Knowledge Base access is unavailable. There is no swarm, AgentCore requirement, deployment or cloud provisioning.

OpenAI Decisions runs five named predicate checks when explicitly enabled: source support, neutrality, jurisdiction, clarity, abstention. Missing, malformed, refused or low-probability results block release. Probability threshold 0.95 is provisional and uncalibrated. A result is a fallible estimate, not a factual guarantee. Offline injected transports are explicitly labelled `offline_stub`; real transports are labelled `real_api`.

GPT-Live is distinct from Realtime: gpt-live-1, POST /v1/live/sessions, WebRTC SDP, client delegation. Browser code waits for session.started and never sends session.start over WebRTC. Transcript fragments are accumulated but never treated as an automatically actionable complete question. Visitors review/correct the transcript before submitting; delegation IDs are correlated and duplicates ignored. Output audio is not attached to a player and remains muted. **Supported spoken answers, full-duplex interruption and buffered audio review before playback are unfinished and untested.** A transcript-only check cannot establish what a voter heard. One session creation per server run limits accidental repeated billable starts; final usage may be unconfirmed after an interrupted startup/close.

## Opt-in integration setup — only after spending authorization

An existing permitted OPENAI_API_KEY must already be available to the backend. Do not paste keys into the browser or this repository. No credential creation/storage step is included. OpenAI SDK 3.28.0 was installed locally with uv; see the actual live results in runtime-proof-2026-10-10.md. Prepare the optional dependency with `requirements-live.in` when installation is needed. HTTP adapters themselves use the standard library and do not depend on SDK example versions.

Set OPEN_ORACLE_ALLOW_LIVE=1 only after approval of model use and budget. Set OPEN_ORACLE_MODEL to an approved model supported by Strands' OpenAI provider; no model is selected by default. Then use `--live` for Strands plus real Decisions, or `--decisions` for exact-source responses with real Decisions. `--live --live-voice` additionally enables the microphone preview, restricted to a loopback host. The preview still holds all generated audio muted. Session creation itself is billable. Real OpenAI Strands/Decisions and GPT-Live transport tests have now run; see `docs/runtime-proof-2026-10-10.md`. Both gated evidence trials withheld their answers after review rejection. Spoken answer and translation alignment remain unverified.

For the Pi browser, plain LAN HTTP is not a secure getUserMedia context. Use a localhost SSH forward or an approved TLS setup before microphone tests. Do not copy backend credentials to the Pi. The Mac browser is the validated local fallback. Camera, wave activation, physical five-inch readability and hardware audio remain unverified; the user reports a live Lumina picture on Mac; physical Pi cable/detection is unresolved. The Pi OS/setup task is untouched.

## Verification and next gates

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -v
node tests/test_live_events.cjs
node tests/test_live_lifecycle.cjs
node --check web/app.js
node --check web/live.js
PROMPTFOO_DISABLE_TELEMETRY=1 promptfoo eval -c promptfooconfig.yaml --no-cache
```

Unit tests include the actual Strands SDK using an offline tool-event provider; this does not prove a live provider round trip. Promptfoo uses an application-owned Python adapter; native Decisions/GPT-Live providers are not assumed. The 51 authored local cases validate source fidelity and boundaries of this slice. Live review remains uncalibrated. Two gated evidence trials rejected release; the receive-only GPT-Live lifecycle succeeded. Continuous voice, spoken alignment and physical Pi frontend tests have not run. Inspect real traces and labelled errors before expanding metrics or claiming reliability.

The current layout applies the common Opus/Sol simplification guidance: one column, system type, one card and source disclosure. No final concept is selected; Daniel’s independent Concept B and direction choice remain pending. A sibling integrated a locally bundled official ElevenLabs UI Orb as a small React/WebGL presence island with CSS/reduced-motion fallback. No ElevenLabs hosted service is used; see docs/orb-and-structured-answers.md. The indicator denotes application state, not factual verification. Reduced motion is supported. Generated mockups and Library delivery are separate from the functioning application.

Before the October 11 08:00 Central submission, leave time for a three-minute recorded working-app video and upload; the live demo is separate at 09:00. Demonstrate only verified capabilities and clearly identify exact-source fallback, live interfaces and remaining voice/source gaps.

## Primary API references checked October 10, 2026

- https://developers.openai.com/api/docs/guides/decisions
- https://developers.openai.com/api/reference/resources/decisions/methods/create
- https://developers.openai.com/api/docs/guides/decisions-voice
- https://developers.openai.com/api/docs/guides/live
- https://developers.openai.com/api/docs/guides/voice-webrtc?api=live
- https://developers.openai.com/api/docs/guides/live-delegation
- https://developers.openai.com/api/docs/guides/voice-server-controls#check-speech-before-playback
- https://developers.openai.com/cookbook/examples/audio/voice_agent_evaluation

Official minimum example SDKs are Python 3.26.0 / JavaScript 7.30.0. The parent's current reference check permits public HTTP image URLs for Decisions; an older guide/skill contract said otherwise. This app sends text only. That dated assumption is recorded here without modifying the external skill repository. The requested better-decisions skill was not locatable in this execution environment; its supplied commit reference alone does not identify an installed SKILL.md.

AWS readiness handoff: existing event authentication and SDK imports work; catalog/runtime/log-group read checks succeeded. Knowledge Base listing, inference-profile/availability inspection and CloudTrail listing were denied. Those denials were respected. The later two bounded event-model smoke requests succeeded; earlier denied reads were not bypassed. The $1 smoke authorization is consumed. Credit coverage and exact charges remain unconfirmed. No resources were provisioned. Runtime review and OpenAI evidence are recorded separately.


## Candidate-source boundary

The pinned bounded source catalog maps all 62 printed nominees and 11 retention judges to exact contest identities. 38 people have source associations; 15 retained current judicial-survey PDFs are available. Auditor/VOTE411 and most Beacon answers remain source pointers. A later preparation step retained four full same-question Beacon answers for Pollard and Fields, covering priorities and property assessments only; see `docs/two-paths.md`. Links are navigation, not indexed position evidence. Nonresponse and mentioned-not-surveyed metadata are distinguished. Government record gateways include historical service and are not analyzed current voting histories. Judicial evaluations belong to their attributed third-party publishers; the app does not issue ratings or recommendations. Missing catalog files or changed hashes produce explicit source gaps. No new candidate pages were downloaded in this step.

## First adaptive explanation card

COMBAT has one predefined server-owned measure_explanation card. It appears only after valid current-snapshot evidence selection/read and exact whole-passage matching. Five facets explain the decision, unchanged literal rate, ten-year continuation, stated purposes and separate trust fund, each with a quote and offsets into the released passage. YES/NO is bounded to approval/rejection of this question's continuation; other legal effects are not inferred. Overview and step_by_step contain identical statements and anchors.

The answer surface shows one COMBAT part at a time. Previous/Next buttons and focused-card presenter arrows navigate its pinned facets. Typed confusion or YES/NO follow-ups reuse the latest supported contest only within the current visitor context. Historical requests, ambiguity, source gaps, recommendations, invalid selections and review rejection cannot release the card. Reset clears context and late results. Strands still selects actual evidence when live mode is explicitly enabled; card choice is deterministic, not claimed as a model-generated UI. The entire card is included in the Decisions envelope before release. Default AI review is not run and plainly labelled. Model voice/audio does not play this explanation yet.

## CopilotKit decision — October 10, 2026

Evaluated official Strands introduction/quickstart and controlled tool/state rendering documentation. The documented integration uses a React frontend, CopilotRuntime/HttpAgent HTTP connection and ag_ui_strands bridge. Current app is vanilla JavaScript plus stdlib HTTP, with a narrow evidence gate. For this first card, preserve that renderer and explicit response schema: a React/AG-UI migration would add a new surface and streamed-release boundary that needs verification, while voice remains unfinished. This initial decision is superseded by the later actual controlled CopilotKit route described below; the full generated sandbox remains disabled. No hosted Intelligence account, telemetry service, new credentials or A2UI model call was introduced. A future opt-in bridge must publish only accepted evidence/card envelopes; raw model text and tool streams cannot bypass the Decisions/grounding gate. This is a deadline/scope decision, not a claim that CopilotKit lacks Strands support.

Primary sources: https://docs.copilotkit.ai/strands ; https://docs.copilotkit.ai/strands/quickstart ; https://docs.copilotkit.ai/strands/generative-ui/tool-rendering ; https://docs.copilotkit.ai/strands/generative-ui/state-rendering .

Current integration assessment and narrow unexecuted network proposal: [integration decisions](integration-decisions-2026-10-10.md). Speech remains held until the [release contract](speech-release-contract.md) has actual playback evidence.

Later checkpoint: the direct approval retry and concrete failed quality controls are recorded in runtime-proof-2026-10-10.md. The optional /copilot route is now an actual local CopilotKit/AG-UI controlled integration; see copilotkit-local-integration.md. No full Open Intelligent UI sandbox, live checked answer or speech success is claimed.
