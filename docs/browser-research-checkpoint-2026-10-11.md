# Browser research checkpoint — October 11, 2026

The main browser now has an explicit opt-in real Strands research route. Both
`/api/ask` and buffered `/api/ag-ui` use `ResearchEvidenceLoop` when started with
`--live --research --max-live-requests N`. Default startup remains the existing
exact-source loop. Research requires an explicit KCEB/JCEB selection and supports
only the reviewed COMBAT rate, duration and unsupported-crime-prediction refusal.
Unrecognized or additional requests are refused in full, rather than silently
dropped. Candidate research and arbitrary generated explanation remain pending.

Strands owns planning, query formulation, scoped source discovery, hash-checked
archive acquisition, FTS5 chunk search, separate reads for each part, and cited
structured output. The application owns finite explanation forms, trusted source
metadata and release validation. This is substantive agent retrieval with checked
wording templates, not an unrestricted agent-written comparison. No semantic
encoder, Bedrock KB, AgentCore deployment or new provider credentials are added.

The browser display adapter is a separate explicit contract. It rebuilds complete
COMBAT context from the correct authority's registry, including the trust-fund
condition, and exposes the retained original through the existing hash-checked
route. Registry research IDs are not inserted into the older JCEB contest-evidence
catalog. Every visible field is projected before Decisions, reprojected after it,
and independently rebound before display/AG-UI. Raw research-service shapes fail
closed gracefully, rather than crashing on a missing `contest_id`. Speech remains
off for this route. Erase signals cancel in-flight research/review and block late
display. The browser work deadline is 35 seconds, below its 40-second UI deadline;
provider timeout is 10 seconds, no retries, maximum12 model turns. The 24,000-token
soft bound is checked between calls; it is not a hard invoice cap and one prior
8-call trial accumulated27,759 tokens before finishing.

## Actual main-browser results

All fixed public fixtures were entered using the real browser composer/context
controls on a new owned loopback server. Headless Chrome does not establish
physical Pi or audible speech acceptance. No media capture/playback, external
browser assets or desktop/Pi browser takeover occurred. Each server was capped
and stopped afterward. The existing8765 exact-source process stayed running.

| Browser fixture | Strands calls | Decisions calls | Result |
|---|---:|---:|---|
| Initial rate+duration |8|1|Held: source0.99, jurisdiction0.93, clarity0.85; unchanged0.95 gate |
| Crime reduction by20percent |4|1|Accepted refusal; no supporting factual claims or acquired source |
| Rate+duration, explicit approval condition and publisher label |6|1|Accepted/released; source/jurisdiction1.0, clarity0.97 |

The released answer: “If approved, the COMBAT sales tax would continue at
one-quarter of one cent. If approved, the COMBAT sales tax would continue for ten
years.” The DOM exactly matched accepted text. Complete original and trust-fund
condition were visible; the locally fetched PDF matched the retained JCEB hash.
The refused prediction also matched its accepted visible text. Further requests
received429 at the configured cap. Evidence is retained in
`evals/browser-research-20261011/`. A first harness stopped at a collapsed context
selector before submitting any request: zero model/Decisions calls. The corrected
harness passed an offline SDK browser rehearsal, then used the untouched existing
reservation. No provider operation was retried.

Shared reservations at this checkpoint: **$13.15/$50**, **$36.85 unallocated**.
These are allocations, not confirmed billed spend. Decisions remains fallible;
the differing accepted/held results demonstrate why a score is not factual
certainty and why a passing fixture does not validate the judge generally.

## Scope and next fixes

The working default fallback still needs the independently reported natural
candidate routing, contextual property follow-up and supported/unsupported-part
accounting fixes. Candidate originals are retained but phrase routing is not
evidence absence. Those changes have separate owners/restore points. Current
America.gov styling is retained per Daniel's latest choice. No SVG was selected.
Camera wave/thumbs/swipes remain staged with their device owner; this checkpoint
adds no sensor capture. Human Play/device checks await their applicable readiness.

## Test audit and local Git discipline

Applied the installed
`/Users/danielgreen/.codex/skills/test-audit/SKILL.md`, whose upstream is OpenClaw's
test-audit skill. This repository uses Python unittest, authored offline Promptfoo
and native local browser tests, so OpenClaw-specific commands were not run. New
tests guard independent browser schema/provenance, unreviewed AG-UI rejection,
multipart coverage, no-model clarification/refusal, cancel/erase, both actual HTTP
transports and the request cap. Existing source/refusal/privacy tests remain;
none was deleted to reduce a count. Existing stronger fixtures are reused.

The wording/install refinement was initially rejected by automatic approval review
because it appeared to remove an AG-UI research review branch. The proposed diff
actually retained that branch and restored the stricter legacy branch. Independent
staged-module checks rejected six unreviewed release cases; the evidence-backed
install then succeeded. A status message to the parent was rejected separately;
the normal final handoff remains available. No workaround, publish or push occurred.
