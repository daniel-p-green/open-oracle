# Open Oracle startup and end-to-end acceptance

Checkpoint: 2026-10-11 02:10 UTC. This runbook describes current code, not a new deployment or selected design. Tunnel and physical-device execution belong to the hardware owner. Forwarding approval and recognized direct paid-trial approval are separate pending prerequisites. Do not activate autostart, paid modes or sensor capabilities as a side effect of these instructions.

## 1. Reproduce the safe Mac startup

Use the existing project and Python environment; no install, secrets or cloud profile is needed for exact-source mode. From the Mac project:

```sh
cd /Users/danielgreen/Documents/Codex/open-oracle
.venv/bin/python --version
.venv/bin/python -m open_oracle.server --help
lsof -nP -iTCP:8765 -sTCP:LISTEN
```

The current listener is task-owned PID 26672, 127.0.0.1:8765. If present and healthy, reuse it. Never kill an arbitrary listener or launch a duplicate. If absent, start in a foreground terminal:

```sh
.venv/bin/python -m open_oracle.server --host 127.0.0.1 --port 8765
```

Expected startup line includes exact-source mode; no model calls. No --live, --bedrock, --decisions, --live-voice, --sensor-stdin or capability flags belong in this baseline. Existing environment values cannot enable those CLI flags automatically. Do not print environment or credential contents. A confirmed operator name can later be supplied with --operator-name; do not invent it. Ctrl+C shuts down the foreground process. No persistent service is installed by this runbook.

If the environment is missing, stop and report that dependency prerequisite. The repository has pinned requirements and earlier setup instructions, but this checkpoint does not install packages or fetch dependencies. The Mac .venv is Python 3.12; do not copy it to the ARM64 Pi. Pi browser operation does not need the Mac backend's dependencies installed on Pi.

## 2. GET-only check of an existing loopback instance

```sh
.venv/bin/python scripts/run_local_acceptance.py \
  --check-running http://127.0.0.1:8765
```

This mode only sends GET requests. It refuses non-loopback URLs and redirects, ignores proxy configuration, does not start a browser/server, submit questions, request media or call a provider. It checks health, main/Copilot/operator pages and critical assets, both retained PDF hashes, no-store responses, Host/Origin rejection and the disabled sensor endpoint. A nonzero exit is a failed checkpoint; never reinterpret it as live readiness.

Required safe health: ready, exact_source, provider null, independent_review not_run, voice not_connected, voice_session_available false, input_events.enabled false, election_date=2026-11-03 and both source_integrity entries true. Current inventory is 55 contests, 62 candidates, 11 retentions, 10 measures. Inventory is countywide retained research, not proof of an individual's complete ballot. operator_name is currently null and the UI honestly reports an unconfigured operator.

The script's CLI/HTTP checks do not prove browser secure context, actual display legibility or capture readiness. On Pi, run its GET-only mode only if the script is deliberately transferred by the owner; it uses Python standard library only. Pi native curl can also read /api/health, but curl alone does not perform the full checks.

## 3. Repeatable isolated offline acceptance

```sh
.venv/bin/python scripts/run_local_acceptance.py
```

This creates an owned ephemeral 127.0.0.1 exact-source server, validates its health, then runs the existing browser regression logic on / and /copilot. It cleans up only its own child server. Evidence is printed with a fresh temporary directory containing http-health.json, browser-current.json and two reset screenshots. To retain it elsewhere, supply --output with a new, unused directory. Existing evidence is never overwritten by the launcher.

Current Mac prerequisites: Node on PATH, the existing Playwright package at /opt/homebrew/lib/node_modules/promptfoo/node_modules/playwright, Chrome at /Applications/Google Chrome.app/Contents/MacOS/Google Chrome, and project .venv. The script fails before execution if these are missing and installs nothing. It is not a portable physical-Pi browser driver.

The browser check explicitly forbids microphone capture and external/provider browser requests. It checks keyboard-labelled submission of What is the COMBAT tax rate?, the exact answer The printed tax rate is one-quarter of one cent., source disclosure preserving the full retained quote, matching original-PDF SHA256, attributed Pollard/Fields priorities, reset/late-response rejection, logical 800×480/320×700 reflow, 48px submit target and reduced motion. It is targeted acceptance, not a complete accessibility audit, actual audio test or physical display validation.

The existing offline code checks remain:

```sh
.venv/bin/python -m unittest discover -s tests -q
node tests/test_interaction.cjs
node tests/test_live_lifecycle.cjs
node tests/test_live_events.cjs
node tests/test_buffered_voice.cjs
node tests/test_input_bridge.cjs
```

Latest results: 88 Python cases, 26 interaction groups and the four other Node suites pass. HTTP tests need permission to bind temporary loopback sockets; a restricted shell PermissionError is not a product verdict. Use the permitted local test execution environment rather than weakening networking or security. No paid tests are invoked by these commands. pytest is not installed in this environment; unittest is the actual passing runner.

## 4. Pi connection and text acceptance — hardware owner, after forwarding approval

Follow docs/pi-connection-and-review-2026-10-11.md and scripts/pi_tunnel_plan.py. Refresh the Pi address/account and authenticate the host fingerprint through the existing Pi control route. Historical user/address dg@192.168.234.5 are not permanent device identity. Strict host trust/login remain incomplete. Human authentication and any trust setup must follow the applicable approval; agents do not enter/extract/store secrets. No forwarding has been executed by task-2.

The proposed temporary reverse forward makes the Mac loopback app available at Pi http://127.0.0.1:8765/. Verify a Pi loopback-only listener and that the actual app opens. Leave firewall, GatewayPorts, venue exposure, certificate/debug flags and persistent autostart unchanged. The Mac app cannot be reached by using Pi localhost without the approved forward.

Exact supervised Pi text script:

1. Open the actual loopback URL in the owner's Pi browser. Confirm the expected prototype/operator notice and November 3 scope. Inspect readable text/source controls at actual 1280×720/scale 1 and the viewing distance. No horizontal clipping or shrunken functional text.
2. Type What is the COMBAT tax rate? and submit Show evidence. Expect the printed-rate sentence and an explicit sample/personal-applicability limitation. Voice remains disabled; independent AI review has not run in this mode.
3. Open Sources (1) and limits. Confirm actual original wording and publisher; open the retained original PDF. Close/return without losing the accepted answer. A retained PDF is not a confirmed personal ballot.
4. Ask Compare Pollard and Fields priorities. Confirm each candidate's answer is attributed and both receive equal visual treatment. Do not present the text as independent endorsement or confirmed policy effectiveness.
5. Use Start again. Confirm question/answer/source content is cleared. Use the keyboard route if available to verify focus/submit/return without a pointer. Record a result rather than declaring full accessibility compliance.
6. If forwarding disconnects, treat app unavailability as a failed connection. Reconnect only the authorized session through the owner and rerun health. No boot/recovery proof exists until an actual coordinated recovery is observed.

## 5. Named-device readiness — separate bounded capture approval

After the owner has approval for the specific local preview, open /devices. Before Start, confirm browser secure context and media API in the page; no capture should start automatically. Select explicit labelled Lumina camera and microphone IDs, refresh after a deliberate permission grant if labels are absent, and press Start 30-second local check. Default/unlabelled devices are rejected. Inspect real preview and mic meter, then Stop or allow the 30-second limit. Confirm the camera indicator and capture tracks stop; leaving the page must also release them. No recordings/upload are part of this page.

This establishes local Pi browser capture only. It does not establish app voice provider behavior, spoken turn completion, model support or audio audibility. Pi owner's separate guvcview preview and Daniel's microphone-meter confirmation are already hardware facts and need not be repeatedly troubleshot.

Current audio route: PipeWire HDMI sink alsa_output.platform-107c706400.hdmi.hdmi-stereo, unmuted, 40% sink volume. Packaged paplay test returned 0 but audibility remains listener-unconfirmed. The owner can use the already staged bounded sample test only within its authorization; do not reroute/change persistent gain here. Raw ALSA default error 524 is retained and is not evidence of browser-output failure or success.

## 6. Real provider/audio acceptance — paused until recognized direct paid approval

No command in this runbook enables live mode. The already prepared bounded public-COMBAT proof is separate and remains unexecuted after two approval-review rejections. If direct consent is accepted, the owner follows that exact approved trial and cap, preserving the 0.95 threshold, mechanical source guards, buffered speech contract and no retries. Do not silently reroute to a different provider or restart to evade a used allowance.

Acceptance requires actual current Strands retrieval/selection, actual Decisions response, release/withholding status, one actual GPT-Live session, complete buffered provider transcript, bound same-language display and human comparison of audible words to the accepted sentence. If quality checks withhold or fail, record that result; original-source fallback does not prove accepted model speech. Prior historical receive-only sessions and authored offline fixtures are separate evidence.

Only after microphone capture permission is also applicable: Speak, deliberately grant the named mic, say What is the COMBAT tax rate?, review/correct the actual transcript, submit Show evidence, and use Play answer only when the bound output is accepted. Stop/Start again must immediately stop capture/playback and clear transient content. Record Stop/reset behavior and any delayed output; do not store visitor recordings or transcripts in proof artifacts. Provider retention is not verified. Translated voice, hands-free spoken correction and full-duplex follow-ups remain unsupported/unverified.

## 7. Physical gesture and fully embodied acceptance — separate producer readiness

Use the hardware owner's staged, bounded camera test under the informed privacy decision. Current MediaPipe/OpenCV runtime and generated temporal cases pass; physical waves/false triggers have not. Vendor terms describe telemetry and separate model redistribution licensing is unresolved; local frame processing is not a zero-egress claim.

Physical checks must reject stationary hands, incidental movement, non-hand motion and repeated starts while active; deliberately initiated waves should trigger once. Production capabilities stay disabled until those checks pass. A ready/frame event alone is neither presence nor intent. Current staging must supply actual continuous frame heartbeats and separately validated presence/loss/departure before the complete lifecycle is enabled; do not synthesize missing presence.

After authorized transport and verified producer capability, acceptance is approach → invitation without capture → deliberate intent → actual listening → corrected accepted question → supported answer and actual speaking → source request/follow-up → confirmed departure/reset. Test departure during listening, retrieval and playback; late provider/source events must not restore previous visitor content. Camera failure becomes unknown, not fabricated departure. Physical false-trigger calibration, hands-free turn completion/source requests and full boot recovery are blockers, not passed rows.

## Evidence and recording checkpoint

evals/startup-acceptance-20261011 retains the actual fresh isolated offline run. evals/lifecycle-review-20261011 retains Opus and fixture regression evidence. The core app remains safe exact-source mode. No physical checks, tunnel, capture or paid trial were performed in this documentation pass.

Do not label the recorded demo as hands-free, live voice, physical wave or reviewed-model output unless those exact routes pass. Use the functioning sourced-text fallback honestly if they remain blocked. Preserve time for the three-minute recorded working-app video and upload before the stated Sunday 08:00 Central deadline, plus the separate 09:00 live demo. No recording/upload/submission is authorized by this runbook.
