# Open Oracle: reviewed implementation and concrete Pi connection checkpoint

## Ownership and current runtime

Daniel directly redirected task-2 to critique Claude's design explorations, develop a detailed NDS-inspired simplicity brief and generate a few visual concepts. That request is completed in design-reset/simplicity-iteration-brief.md and three simplicity-*.png files. No direction was selected and no application styling was integrated for that study. This checkpoint resumes the preceding implementation assignment; no further design generation is planned.

Fresh listener inspection and HTTP health confirm the Mac app at http://127.0.0.1:8765/, PID 26672, bound only to 127.0.0.1. Mode exact_source; both retained ballot integrity checks true; independent_review not_run; voice not_connected; voice_session_available false; input_events.enabled false; operator_name null. There is no verified Pi-reachable URL. The owned temporary regression server at 8766/PID21899 was stopped after tests. No venue-network exposure was broadened.

## Actual Claude review and applied changes

An actual existing-subscription Claude CLI call completed successfully with canonical model claude-opus-5-5, --effort high, tools disabled and relevant allowlisted source supplied through stdin. Raw report opus-review.md/json and pre-review manifest are retained. Model metadata reports list-basis cost $1.41602, not verified separate billing; this is not an OpenAI budget debit or evidence of a paid OpenAI trial. This was static code review, not reviewer-executed tests or certification of answer correctness.

Applied fixes include immediate local reset independent of delayed provider close; synchronous transient transcript/audio discard; cancellation of pending microphone permission and SDP fetches; generation/token rejection of stale callbacks; accepted-output checks on indirect speech paths; speech/pause/replay state repair; stable focus through answer-part changes; preservation of typing through repeated presence events; visible capture disclosure and Stop outside the collapsed fallback; voice-slot preflight and truthful exhausted-budget messaging; readable-invitation timing; stale-presence expiry to unknown; malformed event rejection and adapter recovery. Source/release gates remain in place.

Fresh verification: 88 Python unittest cases pass with temporary loopback test fixtures permitted. 26 interaction groups pass. Offline live lifecycle, live event, buffered voice and input-bridge Node suites pass. app.js/live.js syntax checks pass. No paid provider calls or physical media capture occurred during these checks.

Retained actual-browser evidence records passed keyboard/focus/reset cases with explicit voice/close fixtures, including a six-second close that does not block typing or clear a new answer. Browser stdin evidence exercises actual Python stdin → HTTP → browser adapter with authored metadata fixtures. Operator device evidence exercises explicit fake device/permission/audio fixtures and a scaled timer. Each record explicitly disclaims physical sensor or capture proof.

## Concrete transport and operator code present

Canonical server accepts opt-in --sensor-stdin and serves a read-only same-origin /api/input-events poll. Its bounded metadata reader checks session, sequence, timestamps, event/source pairs and explicit synthetic=false; image/audio/text payloads are not carried. There is no HTTP injection endpoint. A ready event is not frame proof: frame heartbeat leases expire to unknown, not departure. Presence/wave/local-wake capability flags are separate, default false and require stdin. Metadata schemas are not authentication or proof of physical intent.

The browser input bridge feeds the guarded interaction adapter and rejects bootstrap replay/discontinuity/stale streams. A fresh producer session is required after relevant reconnect/reset conditions; full boot recovery remains unverified.

The separate /devices page requires deliberate selection of named camera and microphone IDs. It offers a bounded 30-second local preview/meter, Stop, late-permission cancellation and track cleanup. It has no media recording/upload/persistence. Only fixture tests have run on this page; actual Pi browser capture is still pending authorization and connection.

## Next connection step — proposal only, not executed

Keep the Mac backend on loopback. Use the Pi's existing SSH service to expose it only at Pi loopback through a temporary reverse forwarding session. Historical Pi address/account are 192.168.234.5 and dg; refresh them with the Pi owner before use. Historical authenticated desktop fingerprint was SHA256:UOwjEH4SR62v2lPuBqGk0cZ3N36APcfy56Eh3byY+7M; freshly compare it through the authenticated Pi control route. Host trust and login have not been completed by task-2.

Dry-run-only template pi_tunnel_plan.py produces:

```sh
ssh -N -T -o ExitOnForwardFailure=yes -o StrictHostKeyChecking=yes \
  -o ForwardAgent=no -o ForwardX11=no -o ControlMaster=no -o ControlPath=none \
  -o ServerAliveInterval=15 -o ServerAliveCountMax=2 \
  -R 127.0.0.1:8765:127.0.0.1:8765 dg@192.168.234.5
```

This command must fail if strict host trust is missing. Do not bypass it, change GatewayPorts/firewall/network policy, create keys or configure persistent credentials. If authentication is needed, the human enters it directly; agents do not extract/store secrets. Any initial trust change needs the applicable explicit authorization. Confirm the Pi port is free before connecting.

Once authorized and connected, the Pi owner opens http://127.0.0.1:8765/ and http://127.0.0.1:8765/devices. These are proposed URLs, not reachability proof. Verify actual Pi loopback bind, browser secure context, Host/Origin behavior, layout, named Lumina devices and bounded local preview. Stop the diagnostic after 30 seconds and verify tracks release. Live cloud voice stays disabled under this connection/device-check approval.

One concrete authorization bundle for the parent to coordinate: temporary strict-host-verified loopback forwarding, direct human SSH authentication if necessary, a bounded 30-second named-camera/microphone local diagnostic, and the confirmed supervisor name to display. No paid API calls, persistent autostart, public deployment or broad network exposure are part of that bundle.

## Gesture integration after physical validation

Use the existing Pi Python environment at /home/dg/open-oracle/venv/bin/python; do not duplicate camera ownership or install another runtime simply to connect the app. The prepared path is verified producer JSON-lines over authenticated SSH stdout → Mac --sensor-stdin → same-origin poll → guarded adapter. A producer must emit actual frame heartbeats, separately verified presence/loss/departure and physically validated deliberate wave before those capabilities are declared. Do not manufacture presence from a ready/frame/wave event.

Latest task-6 handoff has an isolated ARM64 MediaPipe/OpenCV open-palm temporal-wave candidate, generated-frame timing/checks and official pinned-v1 bundle hash verification. Physical wave and false-trigger tests remain unrun; production Start is disabled. Complete model-weight redistribution licensing is unverified and vendor terms describe telemetry with no verified opt-out API. Local frame processing is not proof of zero egress. Preserve that distinction; prototype evaluation is not blocked solely by the unresolved public redistribution question.

Pi hardware owner has separately observed Lumina room preview and Daniel-confirmed mic meter response. Those facts do not prove this app's Pi browser capture, gesture path or cloud voice. Physical playback audibility, spoken correction/turn completion, departure calibration and full startup/recovery remain pending.

## Safeguards and paid-integration blocker

The retained safeguards checklist was read. The app has a supervised-prototype/fallibility notice, explicit operator configuration, deliberate activation guards, visible Stop, nonvoice route and immediate session cleanup. Provider retention is explicitly unverified. No analytics/feedback collection was added. This is not a legal compliance or full accessibility certification.

The previously proposed bounded public COMBAT Strands/Decisions/GPT-Live trial remains paused. Automatic approval review rejected the paid external request twice; the second rejection did not accept approval quoted through delegation as direct human consent. No paid command executed. The parent must obtain recognized direct approval before that precise trial is retried; SSH/device approval does not authorize it. No alternate paid route or provider call was used to bypass this blocker.
