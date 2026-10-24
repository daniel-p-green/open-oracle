# Demo references and adaptations

Recorded October 24, 2026, following Daniel's request to explain why and how
references are used. Parent researched these official sources; this record does
not imply a second source-code audit. No demo application code has been copied.
URLs are the reviewed references; an immutable upstream commit/archive digest
was not supplied, so no version is invented. Recheck terms before importing code.

| Reference | Status, reason and actual application | Evidence and limits |
| --- | --- | --- |
| [Tempo](https://developers.openai.com/showcase/tempo), [source ZIP](https://developers.openai.com/downloads/api-demos/tempo.zip) | **Concept reinforced / applied.** Separate bounded Decisions judgments from grounded Responses, with server credentials, quotas and uncertainty. Existing owners predate receipt of this reference. `experimental/openai-web/journey.py` now distinguishes factual eligibility from delivery quality; `web/journey-core.mjs` and `web/experience.mjs` expose unconfirmed simplicity instead of treating it as factual failure or silently claiming success. | Actual EN overview → simpler → ES adaptation completed; finite adverse-control checks hold. Not independent calibration. No root application LICENSE established; no ZIP code imported. No recommendation/ranking actions or lowering factual gates to force output. |
| [Realtime Solar System](https://github.com/openai/openai-realtime-solar-system) | **Considered, not implemented adaptation.** WebRTC voice-to-visual function-call pattern is relevant to later natural interaction. | Parent verified MIT LICENSE; retain its notices if code is imported. No upstream commit pinned, no source copied, no WebRTC integration claimed. Current Live/Decisions contracts take precedence over old Realtime orchestration. No Spline/heavy scene or invented chart facts. |
| [Chatkit World](https://developers.openai.com/showcase/chatkit-world) | **Concept considered.** Map/chat adjacency supports understanding without memorized geography. `web/experience.css` now places the source journey beside actual maps on wide screens and stacks them on narrow screens. Existing official-map components were already built. | Current 390px journey/office view inspected with document width390; desktop two-column layout visually inspected. This is viewport evidence, not device/assistive validation. No repository/license verified; no copied source or desktop-only exclusion. |
| [Lumen](https://developers.openai.com/showcase/lumen) | **Workflow partly adopted.** Record rendered viewport findings, fix and rerun. `web/experience.mjs` retains action nodes and separate activity/progress regions so late answers do not steal focus or overwrite teach-back. | Real source interaction and a clearly labeled zero-API delayed mock exercised; focus/activity retained. Independent source review closed cleanup-token defect. **No axe scan performed**; keyboard/screen-reader/human dynamic-state acceptance remains open. Root app license unestablished; no code imported. |
| [Loupe](https://developers.openai.com/showcase/loupe) | **Workflow adopted.** Separate applied CSS changes from observed visual outcomes; inspect fresh rendered screenshots rather than treating a patch as proof. | `web/experience.css`, `web/index.html`, `web/map-view.mjs`: quieter progressive source disclosure, explicit original-map links, larger labels, visible Stop. Fresh desktop/mobile screenshots inspected. The real ES-generation proof image predates the visual polish and is labeled accordingly; no image implies heard speech. Root app license unestablished; no code imported. |

The showcase is inspiration, not evidence of election accuracy, source rights,
Spanish civic meaning, acoustic quality or public readiness. Verification and
costs belong in [logs.md](../../logs.md); remaining product gates are in
[DEMO-ACCEPTANCE.md](DEMO-ACCEPTANCE.md). Future code reuse must add its exact
upstream commit, files, license/notice handling and verification here.
