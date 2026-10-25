# Managed trial budget review — October 24, 2026

No paid inference was started during this clarification. The map screenshot was
saved to the user's Library as explicitly requested; its verified Library identity
and local metadata receipt remain outside this public repository. This note
clarifies the managed-trial blocker rather than claiming no server budget controls
exist or demanding a zero-risk guarantee for all API use.

## Controls actually checked

| Control | Documented support / what it establishes | Remaining limit |
| --- | --- | --- |
| No execution environment | `environment.type: none` is documented for supplied-text tasks | Removes hosted sandbox charges, not model-token charges. Initial input is required; creation can start work before the caller has a recoverable ID. |
| No external tools or subagents | Empty tool configuration and `multi_agent.enabled: false` are supported settings | Removes these cost sources. The inspected contract does not promise exactly one internal model invocation per managed turn. |
| Reasoning and structured output | Model-dependent effort and JSON Schema are documented | Low effort and a small visible envelope do not cap hidden reasoning or total managed work. Astra supports low and higher effort; `none` is unsupported. |
| Session usage budget | Errors document `session_budget_exceeded` | This establishes an internal server budget exists. No amount, units, configurable request field or $5-setting procedure was found in the inspected create/configure/reference material. Do not invent `budget`, `max_turns` or `max_output_tokens` for Agents. |
| Cancel and reconciliation | Submit `agent.session.input.cancel`; inspect the root turn's cancelled/completed/failed state and usage; retrieve saved work after disconnect | A successful send is not the terminal cancellation event. Stream closure/local timeout is not a remote stop. No documented maximum cancellation/billing tail was established. |
| Project/organization hard limits | Explicit enforce-hard-limit settings can reject subsequent traffic with 429 | They differ from alerts, but enforcement propagates and can overshoot. No numerical maximum overshoot is documented. These are monthly/shared controls, not a per-session $5 guarantee. No setting or credential was changed; actual current enforced account limits were not re-inspected. |
| Idempotent submission | Reuse the documented event-submission idempotency key on a follow-up retry; reconcile saved work first | Not permission to assume create-session idempotency semantics. Current code never blindly retries uncertain creation; the local ledger preserves late matching IDs without resuming stopped work. |

Sources: [configuration](https://developers.openai.com/api/docs/guides/agents-api/configuration),
[create-session schema](https://developers.openai.com/api/reference/resources/beta/subresources/agents/subresources/sessions/methods/create),
[session errors](https://developers.openai.com/api/docs/guides/agents-api/errors#turn-errors),
[run/cancel](https://developers.openai.com/api/docs/guides/agents-api/sessions),
[terminal events/recovery](https://developers.openai.com/api/docs/guides/agents-api/sessions/events),
[hard spend limits](https://developers.openai.com/api/docs/guides/spend-limits).
The linked schema's HTML was inspected when the docs fetcher's Markdown route
returned 404. Read-only project access was verified earlier; no write/model
entitlement is inferred from that successful list request.

## Expected cost versus possible exposure

A supplied-text, no-tools/no-sandbox, single-turn request is a sensible **low-cost
configuration**, but that is different from a verified $5 ceiling. The
[Agents quickstart](https://developers.openai.com/api/docs/guides/agents-api/quickstart)
uses `gpt-6-astra`; that is a documented example, not evidence this account has
completed an Astra-managed turn. A scenario of 2,000 total input and 1,000 total
output tokens, including reasoning, costs about **$0.07 per model invocation**
at current short-context Standard rates. Managed base instructions and any
additional invocation are not measured by that scenario, so it is not a job quote.

Astra's [model limit](https://developers.openai.com/api/docs/models/gpt-6-astra)
is 128,000 output tokens. At **$50/M**, that allowance alone is **$6.40**, before
input. The managed harness may impose a lower internal ceiling; its value was not
verified. This is a conservative model-limit calculation, not an observed charge
or a claim that every managed invocation can reach 128k tokens. It shows why the
model choice and a short prompt alone do not establish the initial $5 ceiling.
The inspected schema exposes no caller output-token ceiling for that session. Other models may reduce expected/per-invocation cost, but Luna's
managed-harness compatibility and a managed invocation-count bound have not been
verified; its ordinary Responses availability is established separately.

[Pricing](https://developers.openai.com/api/docs/pricing) is usage-based. A local
reservation does not constrain remote computation. If creation or cancellation
outcome is uncertain, the remaining model work can still be billed; its maximum
managed-run amount was not established. There is **no new incurred exposure now**:
no session was created, no new reservation was made and no new inference ran.
The shared ledger remains at $0.55 conservative reservations, with prior usage
estimates unchanged. Raising the sub-budget alone would not establish the missing
managed-run contract.

## Supported next step under the existing budget, not executed

Recommend one application-owned **Responses** extraction using `gpt-6-luna`,
which already worked in the scoped account. This temporarily changes the trial
harness, not the primary-source contracts or live conversation architecture:

1. Send only the retained bundle's short public identity/attributed excerpts and
   typed source IDs. No original containing personal fields, private voter data,
   debate audio, tools, sandbox, subagents, previous response or conversation.
2. Count the **exact same full input/instructions/schema** through the documented
   [input-token endpoint](https://developers.openai.com/api/docs/guides/token-counting);
   hold above 8,192 tokens. Use Standard/default tier and standard reasoning mode,
   `effort:none`, `store:false`, no background execution, and one request only.
3. Set `max_output_tokens:1024`. The official
   [reasoning cost guide](https://developers.openai.com/api/docs/guides/reasoning#controlling-costs)
   says this bounds generated reasoning, visible and formatting tokens. This is
   the server-enforced bound absent from the inspected managed-session contract.
4. Reserve **$0.01** before dispatch; disable retries. At Luna's ordinary
   short-context rates, 8,192 input + 1,024 output is **$0.0013312**. Charging every
   input token at the higher listed 12h cache-write rate of $0.25/M gives a more
   conservative **$0.00256** token estimate. Confirm rates/tier before execution;
   no invoice or account-specific pricing guarantee is implied. No tools means
   no separately priced tool charges. A timeout retains the entire reservation
   and stops further requests; the output ceiling still bounds generation.
5. Validate source IDs, exact spans, attribution, missing coverage and candidate
   scope deterministically. Hold incomplete/refused/unsupported output; keep the
   draft private for human review. Record actual returned usage, not this estimate.

The current request explicitly prohibits paid inference, so this is prepared
advice, not an executed trial. The parent can authorize this bounded harness
substitution within the already approved testing budget; no new key or billing
change is needed. It does not evaluate Agents API's recovery/orchestration.

If the trial must specifically use managed Agents now, the consequential decision
is to accept a **forecasted-cost** run with unquantified cancellation/limit tail,
which relaxes the earlier hard-stop condition. Otherwise obtain a documented,
settable session usage budget whose units and enforcement fit the sub-budget,
or retain the hold. Changing a shared project's billing limit requires explicit
approval and still does not make an exact $5 invoice guarantee because of
propagation. No such account change is proposed as an automatic workaround.
