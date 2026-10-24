# OpenAI web rebuild experiment

Provider-off review slice. No packages, credentials or paid calls required.

```sh
python3 experimental/openai-web/server.py
# Open http://127.0.0.1:8894
```

```sh
node --test experimental/openai-web/tests/core.test.mjs
python3 -m unittest discover -s experimental/openai-web/tests -p 'test_*.py'
```

The exact COMBAT reading copy is reused from `fixtures/official_combat.json`.
The source and curated claim registry are pinned together by a digest. The PDF
artifact digest and reading-copy text digest are distinct. See
`fixtures/provenance.json` and [the decision brief](../../docs/rebuild/DECISION.md).

Only six predefined English question forms are supported. Other wording holds
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
