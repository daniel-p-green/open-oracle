# First two working Open Oracle paths

COMBAT explains the printed November 3, 2026 Jackson County question with five predefined, quote-anchored facets: decision, rate, duration, purposes and separate trust fund. It uses the pinned JCEB sample-ballot passage. Its existing step-by-step follow-up preserves the same wording and evidence. This is an explanation of the ballot question, not a recommendation or a complete legal analysis.

The county-legislature comparison covers **District 1 At-Large: Lance Pollard and Carla Fields**. Two shared questions are indexed: stated priorities and property-assessment fairness. Both complete published answers are shown together, with candidate identity, publication date, publisher and local retained-text links. Statements remain attributed claims; the application does not endorse or independently verify them. A comparison cannot be released with just one candidate, a different question, a different contest, or a changed passage.

## Prepare and run

The existing official research originals remain at `research/HackMidwest2026_research/` and are unchanged. The new publisher archive and passage manifest live in ignored `.local/sources/`; source text is not added to the public repository.

```sh
.venv/bin/python -m open_oracle.prepare_sources
.venv/bin/python -m open_oracle
```

Source preparation explicitly downloads the Beacon page. The web app and tests never fetch it. Preparation verifies four inspected passage hashes before replacement; a publisher change requires source review. Missing or altered prepared files leave the official roster available and comparison unavailable. Current source preparation covers only the two named questions, not every candidate statement in the article.

Use the **Explain COMBAT** and **Compare Pollard & Fields** buttons. The latter offers priorities and property-assessment views. The default mode costs nothing in model usage and labels independent AI review as not run.

## Live AWS Strands

```sh
export AWS_PROFILE=open-oracle-event
export AWS_DEFAULT_REGION=us-east-1
export OPEN_ORACLE_ALLOW_LIVE=1
export OPEN_ORACLE_BEDROCK_MODEL=amazon.nova-pro-v1:0
.venv/bin/python -m open_oracle --bedrock
```

Only enable this after approval for the intended model usage. Daniel authorized **two smoke requests with a combined $1 cap**, not an ongoing billable public demo. Those two requests are complete; the review app remains in default mode. No credentials are stored in this repository. Both live providers now require an existing permitted OpenAI credential and the Decisions gate. If review is unavailable or rejects the response, no answer card or source claims are released. The earlier two AWS smoke calls proved retrieval only and predate this requirement; they are not proof of the gated experience. Exact-source mode remains the visibly labelled no-model fallback.

The actual Strands Agent calls `resolve_contest`, `search_evidence` and `read_evidence`; it selects IDs, and the application releases only server-held source text or predefined anchored explanations. Candidate search is restricted to the application-selected question, and both full answers must be read in the same request. Limits: five model attempts, eight tool calls, 25-second workflow deadline, 500 output tokens per Bedrock call, transport timeouts, no retries. These are request limits, not a general account-level dollar budget or calibrated reliability guarantee. Traces identify provider execution, model and selected source IDs. No CloudWatch export, AgentCore resource, CloudTrail trail or cloud deployment was created.

## Verification on October 10, 2026

- Both live requests returned `answered` using **amazon.nova-pro-v1:0**, real AWS transport, four model attempts each. COMBAT: 5,952 ms; candidate priorities: 5,527 ms. Each required evidence ID was read before release. Sanitized local proof: `.local/aws-path-smoke.json`. Exact billed cost/credit coverage is not confirmed.
- Local Python suite: 43 tests passed, including actual Strands SDK orchestration with an explicitly offline event provider and comparison/source-integrity boundaries. Offline provider tests establish workflow mechanics, independently of the live smoke evidence.
- Authored offline Promptfoo cases: 47 passed, zero failures/errors. The provider uses the project virtual environment explicitly. The initial run exposed a global-interpreter dependency mismatch; that configuration was corrected and the full run repeated successfully.
- Browser checks cover both buttons and property-assessment switching. Source quotes and comparison claims are not model-generated summaries. Current-model quality across arbitrary questions is not established by two successful requests.

## Source and API references

- [JCEB November sample ballot](https://jcebmo.org/wp-content/uploads/11.03.26-Notice-of-Election-Sample-Ballot-Poster.pdf), retained snapshot inspected in the existing research pack.
- [The Beacon questionnaire, Josh Merchant, September 22, 2026](https://thebeaconnews.org/stories/2026/09/22/jackson-county-election-legislature-at-large-pollard-fields-cabrera-peyton/). Publisher says answers were edited for length and clarity. Paragraph/list spacing is normalized without changing words; the original page and answer hashes remain available locally.
- [Strands Bedrock provider](https://strandsagents.com/docs/user-guide/sdk/model-providers/amazon-bedrock/) and [Python API](https://strandsagents.com/docs/api/python/strands.models.bedrock/), checked against installed SDK 1.59.0 constructor and tool workflow.

Voice output, other candidate topics/races, comprehensive legal effects and live judge calibration remain outside this first working slice.
