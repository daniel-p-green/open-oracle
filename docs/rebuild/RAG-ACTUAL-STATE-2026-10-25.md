# Actual RAG path and architecture correction request

Read-only code trace on `7906999` (functional voice code `dec4164`), October 25,
2026. This records the implemented path, not a completed retrieval product.
Architecture implementation and paid voice experiments are paused for Daniel's
requested Opus 5.5 consultation.

## What is implemented

| Boundary | Actual implementation and evidence |
| --- | --- |
| Corpus/provenance | `experimental/openai-web/fixtures/proposition-a.json` records KCEB public sample W1-P7, November 3 election, official PDF URL, page 2, retrieval October 24 at 04:32:39 UTC, original PDF SHA-256 and extracted question hash. It explicitly denies personal membership authority. |
| Integrity and freshness | `journey.py:76–82` checks the fixture's hardcoded whole-file hash and embedded question-text hash; `:206–207` rechecks before release. This detects local drift, **not** new official versions or litigation changes. Separate UI map-status record has a review deadline (`web/measure-source.mjs:37–59`); that status is not a source in the generation packet. |
| Extraction/chunking | The question sentence was manually extracted/visually checked from the retained PDF, with normalized line wrapping. No general parser/chunking/index worker runs in this journey. |
| Retrieval | `journey.py:149–152` always loads that one question. `source_packet():85–90` supplies the complete question sentence, application-owned Yes/No interpretation and application scope limits. No embedding/vector store, full-text index, File Search, web search or multi-document ranking is called here. |
| Actual request | `request = OPERATIONS[operation]` at `journey.py:152` substitutes a generic brief/overview/simpler/detail/limits template. Prior context is only a validated prior generated unit (`:154–158`). The actual current user's question is absent. |
| Voice routing/context | Native Decisions hears Live audio/context and chooses view, map focus, delivery and response language (`voice_agent.py:82–109`). It calls Journey with operation/language/prior only (`:251–252`). Independent bounded input ASR (`:293–313`) owns input captions; it does not supply the question to generation. This loses information between native routing and grounded explanation. |
| Generation | Responses (`journey.py:170–176`) receives the generic operation, language, fixed packet, prior checked draft and allowlisted presentation components. `store:false`; no source/URL tools are enabled. This can generate fresh wording, but not reliably answer an unanticipated follow-up. |
| Grounding/release | JSON schema and deterministic source IDs, number admission, attribution, time/scope and polarity-slot checks (`journey.py:94–135`), plus separate Decisions review (`:190–205`). Review permits faithful paraphrase (`:68–69`); .95 thresholds are uncalibrated. `attributed` is advisory; request fit is advisory for detail/simpler. These limitations are not semantic guarantees. |
| Citations | Generated sections name application-approved packet IDs. UI source authority comes from separately hash-checked local source records, not a model-generated URL (`web/journey-core.mjs:102`). UI original access includes exact wording/page/source. This is bounded citation binding, not a general claim-to-passage retrieval service. |
| Missing evidence | Native choices include clarify/abstain/limits; application text refuses recommendations/personal membership (`voice_agent.py:234–244`). Generation can hold on invalid/unsupported output. But the generic request means no reliable explicit coverage decision for an arbitrary actual question. This is a gap even if a generated generic summary is factually supported. |

## Confirmed disconnected evidence

`fixtures/kc-public-sample.json:861–875` retains Proposition A's complete printed
wording, including its separate fiscal note: state and local governmental entities
estimate no costs or savings. `web/measure-source.mjs:17–33` cross-checks source PDF
hash, page and question prefix and exposes `complete_wording` and
`printed_fiscal_note` to the UI. The generation packet omits this note entirely.
It cannot answer a fiscal-note question using that retained evidence today.
The omitted material is the separate note; `proposition-a.json` does contain the
complete question sentence.

The 55-contest printed-notice union and 25-contest KCEB public sample are separate
UI/inventory assets (`web/office-source.mjs:56–57,98–99`). They are not searched by
JourneyPipeline and do not establish every individual ballot style or current
certification. Candidate/office evidence has no general connected retrieval path
in this voice journey. No county-wide RAG completion claim is supported.

`PRIMARY-SOURCE-ARCHITECTURE.md:26,34–37` proposes immutable objects, SQLite
metadata/full-text passage indexes, admission, scope filters and refresh/invalidation.
Those are plans. `research/evidence.py:68–76` implements a SQLite **job ledger**
for idempotence, not a passage index.

## Corrected product contract and review questions

Daniel clarified at 03:49–03:50 UTC that paraphrase is acceptable, explanations
must be clear, and exact repetition was never requested. At 03:57:03 he asked
for Opus 5.5 architecture consultation; at 03:57:45: “We need to stay source
grounded but flexible and with guardrails.” The separate verbatim narrator
proposal is superseded. No renderer was implemented or paid experiment run on it.

The smallest coherent correction to evaluate, **not yet implemented**, is:

1. One application-owned turn request carries the admitted actual public question,
   explicit jurisdiction/measure binding, requested language/detail and relevant
   accepted conversational context. Do not blindly forward private visitor ASR;
   current permitted inputs remain public synthetic questions.
2. Retrieve admitted source passages for that question, including the retained
   fiscal note when relevant. Keep originals/qualifications and exact page/span,
   version/date/rights/scope. Clarify ambiguous binding; abstain on absent evidence.
   Connect the corpus incrementally; do not label a one-measure fix full coverage.
3. Generate a concise natural answer and allowlisted visual arguments from that
   evidence. Enforce numerical associations/units, conditions, Yes/No implications,
   attribution, neutral treatment, request fit and explicit unknowns. Do not impose
   scripted answer templates or exact words as if they were product requirements.
4. Buffer actual Live speech, independently transcribe and semantically validate
   it against the same pinned evidence/request. Accept faithful paraphrase, reject
   unsupported additions or altered meaning. Bind final captions and next-turn
   context to accepted speech, separate from its earlier draft and official original.
5. Define candidate ownership/completeness and late-chunk invalidation before
   replacing equality guards. Quiet alone cannot establish a whole Live answer;
   preserve controlled playback, turn/revision/source expiry, stop/reset and
   independent usage settlement. Measure safe useful response latency honestly.

Official [Live delegation documentation](https://developers.openai.com/api/docs/guides/live-delegation)
was fetched again: client delegation requires application context; event metadata
does not contain task text; commentary is designed for paraphrasing. Application
[playback controls](https://developers.openai.com/api/docs/guides/voice-server-controls?api=live)
remain necessary before-hearing controls. Neither is a proof of completed speech
ownership, semantic fidelity or measured performance in our implementation.

## Consultation evidence

Existing destination: [OpenOracle application bundle review](https://claude.ai/chat/4c378210-7251-4026-9a90-700a23bc34d3).
Model control visibly confirmed **Opus 5.5 High**. Message 49 submitted one
source-only architecture bundle with the above confirmed failures, Daniel's
clarification, actual partial-paraphrase trial evidence, original requirement
reconciliation and requested minimal migration/acceptance critique. No secret,
environment, raw private trace or unrelated file was attached.

Bundle outside Git: `../openoracle-architecture-consult-7906999.md`, 237160 bytes,
SHA-256 `e7018c530c8fe71694d4eb0b3b2ab22bafb9340312585c6d9160fe11f2c7cecf`.
Oracle was used only for local dry-run/render, not API execution. The initial
attachment click opened a file-source dialog rather than a chooser; inspecting
that dialog and selecting its actual “Upload from computer” control completed
the supported upload. No access denial or alternate host route was involved.
Returned review and dispositions will be recorded separately; submission is not
consultation completion or product acceptance.

**Update:** messages50 and52 returned. The
[consultation record and dispositions](OPUS-ARCHITECTURE-CONSULTATION-2026-10-25.md)
preserve the full initial review and its substantive correction after challenge.
Architecture implementation and paid experiments remain paused for parent review.
