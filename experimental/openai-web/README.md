# OpenAI web rebuild experiment

Provider-off review slice. No packages, credentials or paid calls required.

```sh
python3 experimental/openai-web/server.py
# Open http://127.0.0.1:8894
```

```sh
node --test experimental/openai-web/tests/*.test.mjs
python3 -m unittest discover -s experimental/openai-web/tests -p 'test_*.py'
```

The exact COMBAT reading copy is reused from `fixtures/official_combat.json`.
The source and curated claim registry are pinned together by a digest. The PDF
artifact digest and reading-copy text digest are distinct. See
`fixtures/provenance.json` and [the decision brief](../../docs/rebuild/DECISION.md).

In the default fixture mode, only six predefined English question forms are supported. Other wording holds
with a visible gap. This intentionally narrow parser is a baseline, not natural
language understanding or an AI quality evaluation. No generative text,
Decisions review, GPT-Live, microphone, personal ballot import, candidate/office
coverage or external MCP transport is enabled. Spanish interface preview does
not release Spanish civic explanations. Newsroom coverage cannot establish
personal ballot membership; Missouri currently has no VGC coverage.

Keyboard/buttons use the same request/reset controller; idle reset clears the
tab after two minutes. No saved history, logs, accounts, cloud routes or analytics.
Reset is not secure memory wiping. CSP disables external requests/media and the
server serves only an explicit public file allowlist, bound to loopback.

The experiment is isolated from the stable application. A model or hardware
capability is established only by a later authorized integrated human trial.

The voice-flow preview uses injected fixture permission/capture/preparation/player
adapters. It displays a cloud-data disclosure before simulated consent, stops
fixture capture before source checking, requires the complete matching reading,
and requires manual Play. Stop/reset, question or language changes invalidate
pending work and dispose late handles. It generates no sound; preview text is
explicitly not live captions. Live adapters are rejected by this build.

The authorized API smoke and integrated results are in
[the follow-up record](../../docs/rebuild/CONSENT-AND-API-CHECKPOINT.md). They do
not automatically enable providers or establish a human-heard journey.

## Explicit local provider pilot

The default command remains provider-off. An operator with existing authorized
API access can explicitly enable the fixed public-rate path using a Python
runtime with `requirements-provider.txt` installed, an existing process
`OPENAI_API_KEY`, explicit organization/project scope, a private authorized spend
ledger, and `--enable-openai --max-runs 1`. No key setup or persistent access is
performed by this application. Keep ledger/account values outside Git.

Only `question_id=rate` is accepted; raw typed visitor input is rejected. The
live-example button runs Decisions routing, a constrained Responses selection,
an independent Decisions support check, and GPT-Live audio preparation. Prepared
wording and citation ownership remain application-controlled. This is a narrow
baseline for later generative comparison, not a conclusion against freeform text.

All Live PCM is buffered server-side until session closure, exact full-transcript
match, source/request and final-usage checks. There is no audio playback/download
endpoint or browser media element. Cancellation invalidates local display
immediately; in-flight HTTP calls may drain to their timeout, with usage still
recorded and later stages suppressed. Ready audio/results expire from memory
after two minutes, including when the browser stops polling. No audio is written
to disk. Conservative reservations are retained for unknown billing outcomes.

The public-repository CI workflow runs only fixture/mock/loopback tests with
read-only permissions, pinned official Actions and no model credentials or paid
services. Remote CI success must be checked separately from local passes.
