# Embodied lifecycle — implemented local handoff

Implemented in canonical Open Oracle. This is a sensor-independent coordinator and browser integration, not a claim of physically working presence, wave, hands-free conversation or departure.

## Runtime and ownership needs for parent / hardware owner

The core needs only its existing Mac Python environment and a browser. Start exact-source mode from `/Users/danielgreen/Documents/Codex/open-oracle` with `.venv/bin/python -m open_oracle.server --host 127.0.0.1 --port 8765`. No new Node runtime, OpenCV, MediaPipe or wake library is required on the Pi by this change. The Pi remains browser/mic/camera/display frontend; dependency selection for local camera processing is separate. Do not install libraries speculatively or change network exposure to make the integration work.

A temporary test server ran on loopback 8766 with Live off. It was stopped after passing checks; no8766 listener remains. It is not a Pi-reachable URL. The previous 8765 listener was absent at this checkpoint; do not treat historical PID9237/session36673 as current. Parent must coordinate one active canonical runtime and any permitted Pi connection.

Parent reports Daniel verified the Lumina microphone input meter responding to speech on the Pi, and reported guvcview camera preview at15fps. Those are user-verified/reported hardware milestones. Actual app microphone capture, playback, physical wave, presence/departure and live model proof remain unverified in this task.

## Code and integration seam

- `web/interaction.js`: finite lifecycle plus bounded input adapter. No getUserMedia, network listener, sensor simulation, inference or telemetry in this module.
- `web/app.js`: actual capture-ready/review, source-result and playback callbacks update the lifecycle; reset stops tracks/audio immediately, aborts retrieval, clears visitor content and awaits voice teardown. Existing epoch/request and voice release checks remain intact.
- `web/index.html`: coordinator script, honest unavailable-input status and actual transcript region. Typing is a disclosure when a configured presence/voice path is available, and remains usable by default when sensors/voice are unavailable.
- `open_oracle/server.py`: serves the new static script; no sensor endpoint, network bind or Live configuration changes.
- `tests/test_interaction.cjs`: 19 test groups, all offline with explicitly authored event fixtures.

`window.OpenOracleInputs.snapshot()` gives diagnostic state; `reset()` uses the guarded reset. `attachSensorAdapter(options)` is the operator-owned local integration seam, not an installed transport or an authentication protocol. Registration only while idle; one adapter; fresh producer session ID; previous handles cannot control a replacement adapter. Registration requires the producer's current monotonic clock for freshness alignment. No window message listener or HTTP event injection endpoint was installed.

Options: sessionId (8–128chars), producerMonotonicMs, known sources array and explicitly established capabilities (`presence`, `wave`, `localWake`). The returned handle has accept(event) and close(). Closing reports presence unknown and disables sensor invitation, rather than fabricating departure. Capabilities mean externally established readiness, not proof inferred by this class. Hardware owner must verify them before registration; no adapter is configured by default.

Events use existing `open-oracle-input/v1` schema, expected session_id, increasing safe-integer sequence, finite monotonic_ms and mandatory synthetic:false. Reject synthetic/missing flag, stale (>2s), excessive future (>250ms), cross-session, duplicate/out-of-order or unknown type/source pairs. Valid observed events are consumed even if the current state declines them.

Compatible existing pairs: start_requested:camera_wave/presenter_key/presenter_click; reset_requested:presenter_key/presenter_click; error:camera and stopped:camera. Proposed additional producer pairs: presence_detected:camera, presence_lost:camera, departure_confirmed:camera and start_requested:spoken_initiation. The staged wave producer does NOT currently produce verified presence, departure or spoken-initiation events. Do not fabricate those to connect it.

Presence must persist through the provisional500ms UI stabilization dwell before invitation. Repeated detected events do not prevent invitation. This timer is not a calibrated physical detector or departure dwell. Wave intent requires invitation, presence, wave capability and actual voice configuration. Accessible/presenter intent is a separate deliberate fallback. No presence transition calls onIntent or device APIs.

States: idle → presence → invitation → intent → listening → review → thinking → answer_ready → preparing_speech → speaking → conversation; departure/reset invalidates generation and turn tokens immediately. Text/source gaps return to conversation. Source acceptance and prepared audio are distinct from actual playback. Stale tokens cannot advance another turn. Cleanup failure/timeouts stay blocked in reset; no unverified re-arming.

## Sensor choice and wake boundaries

No detector library was adopted. Parent research distinguishes hand landmarks/Open_Palm plus a temporal wave rule from motion-only detection; Wave is not a built-in recognizer class. Presence is separate from hand visibility. MediaPipe's ARM64/Python/OS compatibility and publisher telemetry behavior must be smoke-tested before adoption; on-device inference alone does not establish zero-network behavior.

A local spoken wake option entails an already active local microphone before the conversational session. It requires its own disclosed and permitted setup; it is not equivalent to “microphone off until intent.” No local wake engine or ambient microphone acquisition was installed. localWake remains false by default. Cloud voice still follows the existing capture and paid-authorization guards.

## Actual verification

- 19/19 lifecycle test groups pass: no presence capture, stable invitation, brief-loss cancellation, readiness/intent gates, transcript review, answer/playback separation, stale turn rejection, malformed/synthetic/duplicate/stale input rejection, unknown camera failure, departure conditions, immediate reset and cleanup blocking, departure across listening/retrieval/playback, late-intent cancellation and local-wake gating.
- 76/76 existing Python tests pass, including source, jurisdiction, neutrality, deterministic release, Decisions contract, actual SDK with mocked transport, HTTP routes and Live budget guards. No paid model calls.
- Three existing offline Live event/lifecycle/buffered adversarial suites pass; JS syntax and git diff whitespace checks pass.
- Actual headless main browser with explicit sensor/capture-ready fixtures passes invitation with zero physical capture; synthetic start rejection; one deliberate start; actual transcript display/review; actual local evidence request; departure clearing content and stopping fixture tracks; rejection of that real local response when deliberately delivered after reset. These fixtures do not prove physical detection or microphone capture.
- Both actual `/` and `/copilot` routes pass real local source text/PDF hash/attribution checks, keyboard fallback, reset against delayed real responses, reduced motion and logical800x480/320x700 layout checks. Capture0, Live0, externalrequests0, pageerrors0. Copilot retains its controlled text route; the embodied hooks currently apply to the main page.
- A browser-only unbound timer error was found and fixed before final passing browser runs.

## Remaining gaps

Verified sensor producer + secured local event transport; venue presence/wave/departure calibration; actual app microphone permission/capture; spoken turn completion/correction; conversational follow-up re-arming; voice source requests and interruption; real accepted Strands/Decisions/GPT-Live answer with audible playback. Current transcript confirmation and Play remain explicit fallback controls. The lifecycle does not claim hands-free completion until those paths exist.

Previously denied paid trial was not retried; no new capture or provider request ran. Source/Decisions gates were preserved. No Pi OS, desktop UI, network/firewall, credentials, research or memory changes occurred. Future optional feedback must concern explanation helpfulness/clarity, not vote preference/candidate sentiment; no feedback analytics or raw visitor-media retention was added.
