# Provider-off validation — October 24, 2026

## Automated checks actually executed

- `node --test experimental/openai-web/tests/core.test.mjs`: **10 tests pass**. Six predefined questions; preserved Yes/No scope; candidate/office abstention; injected/forged personal membership records; altered source text/role/hash/URL/scope; invented/missing/extra claims; source/query prompt injection; advice/help/Spanish hold; VGC coverage/disconnection; reset, newer request and idle currentness.
- `python3 -m unittest discover -s experimental/openai-web/tests -p 'test_*.py'`: **5 tests pass**. Real ephemeral loopback HTTP server; every allowlisted asset served; no-store/CSP/media restrictions; truthful capabilities; file traversal/private paths blocked; provider/intake POSTs disabled; unexpected Host rejected. Initial sandbox bind was unavailable; the same loopback test succeeded with reviewed execution permission. No model call was attempted.
- `node --check experimental/openai-web/web/app.mjs` and `git diff --check`: pass.

These are contract/security tests of a finite fixture path, not generative accuracy, model behavior, review calibration, live latency or comprehension evidence.

## Browser observations actually made

The actual served page was opened in the in-app browser at `http://127.0.0.1:8894`.

- Sample Yes/No action displayed all six registered claims. Read source expanded the exact original; supporting-excerpt disclosure showed the bound passage.
- Enter submitted the personal-membership question and displayed the explicit unknown state with no claims. Escape cleared it and restored input focus.
- 320×700 viewport: document width 305px inside a 320px viewport, reading region 273px; no measured horizontal overflow. This is emulation, not a Pi display test.
- Spanish selection displayed a partial interface with a civic translation hold. Example prompts were hidden; Next could not release English civic text as Spanish.
- Browser console inspection returned no warning/error entries at the inspected source-disclosure checkpoint.
- Desktop/source and narrow-viewport screenshots were saved locally outside the public repository.

## Unrun / limits

No paid OpenAI inference, Decisions, GPT-Live, speech/captions, microphone, remote MCP query, actual personalized ballot admission, Spanish civic release, candidate/office content ingestion, physical button, Pi runtime, screen-reader/manual accessibility or performance acceptance occurred. No live adapter exists in this slice. Unsupported phrasing intentionally abstains; semantic parsing is a later bounded evaluation. Whole-corpus digests pin the admitted source and curated text but do not establish official currency or general semantic entailment. Claims are curated experiment copy, not independently reviewed AI output.

The original Hack Midwest checkout was read only and remains dirty on its original branch. The experiment branches from verified public remote main, not that unpublished dirty state; no unrelated presentation PR was changed.
