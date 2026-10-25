# Primary-source candidate architecture and acceptance plan

Status: revised product plan for parent review, October 24, 2026. This supersedes any earlier suggestion that newsroom summaries or Voter Guide Commons form the candidate evidence foundation. The narrow COMBAT provider path is a safety/integration test harness, not the full product definition. No expanded or bulk ingestion/transcription is started by this plan.

## Evidence policy

| Admitted class | What it can establish | Required distinctions |
|---|---|---|
| Election-authority records and official candidate filings | Filed name, office/district/cycle, status and stated filing fields | Filing is not proof that every assertion in it is true; current official ballot determines membership. Match a filing ID where available. |
| Official government records | The recorded action, vote, term, office, document or proceeding | A recorded vote is not an inferred motivation or present campaign position. Bind effective/document dates and jurisdiction. |
| Candidate-authored official campaign material | What the identified candidate/campaign states or proposes | Label as an attributed claim. An official campaign website is not an independent verifier of its assertions. Verify campaign ownership and candidate association. |
| Original debate/event audio or video and official transcripts | What a verified speaker said in the original event | A media-hosted original recording is admissible as the original carrier, not permission to use surrounding commentary, summaries or annotations. Transcript authority, speaker identity, edits and uncertainty remain explicit. |

Do not admit journalism summaries, search snippets, aggregator biographies, third-party surveys or VGC-derived candidate summaries as candidate evidence. They cannot fill an official-source gap. Current approved candidate coverage is **not** nationwide; every jurisdiction/source adapter needs its own admitted scope. Missing evidence produces abstention, not a position, negative inference or a recommendation.

## Separate entities and rights gates

Keep separate IDs/tables for `Person`, `Candidacy` (person + election + contest/status), `Contest`, `Election`, `Committee`, `DocumentVersion` and `EvidencePassage`. Link committees to candidacies only through an official association and its date/version; never merge people, offices or committees on names. Every roster candidate stays visible even with no admitted evidence. Nothing ranks candidates or infers positions from missing coverage.

The [Missouri Ethics Commission FAQ](https://www.mec.mo.gov/FAQ/Questions/) restriction on commercial use of campaign-finance report information was flagged by the owner's primary-source research. Our direct page fetch returned 403; MEC finance ingestion/republication stays blocked until the exact intended use and terms are cleared. Do not treat public access as reuse approval. [FEC guidance](https://www.fec.gov/updates/sale-or-use-contributor-information/) separately restricts use of individual-contributor information; omit donor personal details rather than interpreting a permitted-use exception for this product. No finance data is fetched by this milestone.

[YouTube's captions-download API](https://developers.google.com/youtube/data/reference/rest/v3/captions/download) requires permission to edit the video. Public visibility is insufficient. Use permitted organizer media/transcripts or record transcription as unavailable; do not scrape around that access requirement. OpenFEC and Congress.gov expose supported keyed APIs, but no new key is authorized. No supported Missouri SOS/KCEB/MEC API has been established by this work; jurisdiction adapters must be verified individually.

## Small durable foundation, scalable work units

Use one authoritative evidence store with independent ingestion and serving workers. Start with content-addressed immutable objects plus SQLite metadata/full-text indexes on the Mac; Pi is a thin accessible browser. Keep object storage and a larger relational/search service as replaceable adapters if volume/concurrency later warrants them. Do not build a vector platform, distributed agent framework or nationwide connector before measuring retrieval needs. SQL scope/identity/date filters are mandatory even if semantic retrieval is added.

A source registry owns allowed publishers, exact URL/feed patterns, issuer/event role, publication permissions, geographic/election scope, refresh policy and a human admission receipt. A domain match alone does not establish authenticity or source class. Discovery cannot silently grant admission. Reject arbitrary submitted URLs, redirects to unapproved hosts, private network destinations, embedded instructions and active document content.

Ingestion is a bounded queue of small idempotent work units:

1. **Discover and identify:** enumerate an approved official endpoint, filing register or event listing; save canonical URL, publisher and official record/event ID. Do not guess current coverage from a site title or model memory.
2. **Fetch and version:** enforce MIME/byte/time limits and redirect policy; use ETag/Last-Modified where available. Deduplicate exact bytes by hash and separate changed versions from duplicate URLs. A matching URL does not imply matching content or currency. Keep one provenance edge for each publisher/version even when bytes deduplicate.
3. **Extract:** parse text/PDF/HTML in a bounded isolated worker; preserve original and extraction hashes, parser/version, page and code-point spans. Mark OCR, reading-order problems, missing pages and tables; do not turn partial extraction into a complete source. Keep privacy-bearing fields out of model/index input. Do not retain private voter records, visitor DOB/address or unreviewed personal fields in a public-document derivative.
4. **Transcribe only when needed:** prefer an authentic complete official transcript, checked against the original event. Otherwise first approve a short original recording segment with rights, duration and cost bounds. Record recording hash, timebase, segment start/end, language, model/tool version and exact transcript version. Missing provider confidence is `not_provided`, never an invented score. Distinguish supplied ASR confidence/log probabilities from human verification and from whether a speaker's claim is true. Speaker diarization labels are not candidate identity.
5. **Resolve identity and admit:** bind official filing/record identifiers to candidate, office/district, jurisdiction and election cycle. Names/aliases are hints only. Ambiguous names, aliases, speaker attribution, incumbent/candidate dual roles and changed party/office require a human review queue. Never match using private voter attributes. No source becomes answerable until its identity, role, extraction completeness and citation locator are admitted.
6. **Index and refresh:** index admitted passages with candidate/source/version/topic/scope filters. Fetch incrementally under publisher-specific rate bounds. New or corrected source versions invalidate dependent passage, claim, answer, translation and audio receipts. Keep tombstones and supersession links; do not silently overwrite old evidence. Removal/unavailability changes current coverage explicitly. Retries need bounded policy and must not silently repeat billable transcription or inference.

Raw originals are retained only where privacy and reuse permissions permit; do not promise a complete archival copy merely because a public URL exists. An original with disallowed personal content stays out of general model/index storage; record the source reference and a reviewed redacted/extracted derivative with an explicit limitation. Keep raw visitor text/audio and private ballot records out of this ingestion store. Original debate hosting is not a blanket license to redistribute or train on recordings.

## Provenance and claim retrieval contract

Every admitted evidence passage carries:

- source ID/class and admission policy version; canonical and retrieved URL; publisher/issuer; event/document date and date uncertainty; retrieval time; election/jurisdiction/office scope;
- original object version/hash, extraction or transcript version/hash, supersedes/correction state and access/reuse limits;
- official candidate/filing identifiers where supplied, reviewed cross-source identity ID and review status;
- exact document page/span or recording start/end timestamp and timebase; official transcript versus generated transcript; language, extraction/transcription method and **reported or missing** confidence;
- claim role: recorded fact, filed assertion, campaign claim or debate utterance. None is silently promoted to a broader factual conclusion.

Retrieve an evidence bundle for an explicit candidate/contest/date/topic scope before generating text. The bundle contains same-request read passage IDs, exact locators and coverage gaps. Responses can generate a constrained explanation envelope containing claims, evidence IDs, attribution and uncertainties. Application code validates scope, candidate identity, current version, citation spans, numeric/negation/condition fidelity and actual passage reads. Decisions adds fallible routing/support checks, not authority or claim creation. Refusal, missing/invalid IDs, uncertain identity, conflicting records or unreviewed transcripts hold the affected claims. Sources returned by the model cannot add candidates or contests to an official personalized ballot.

Keep deterministic retained wording as one baseline while evaluating Luna/Sol structured explanations. Compare checked-text speech, Live client delegation and native Live→Decisions on the **same** corpus/questions. The present enum-constrained rate response is a deliberately narrow baseline, not a final decision to abandon generative text. Native Decisions supports routing/classification, not grounded-answer generation.

## Coverage and fair comparisons

Maintain a candidate × source-class × topic × date coverage matrix. Establish the complete relevant candidate set from an admitted authority, not retrieved search hits. A comparison must disclose which candidates have comparable primary evidence, the question/time window used and every gap. Do not omit candidates with absent transcripts or selectively quote only well-covered candidates. If the available material is not comparable, show attributed excerpts separately or abstain from the comparison. Absence, refusal to answer and an explicit contrary statement are separate states; nonresponse must itself have a source.

A correction creates a reviewed new extraction/transcript/identity version, records who/what approved the correction without visitor data, and invalidates affected outputs. Uncertain words, numbers, speaker labels and apparent contradictions need a visible correction workflow with links back to the original page/clip. Do not repair a quotation invisibly or synthesize unsupported word-level timestamps.

## Reuse from Hack Midwest, with limits

`open_oracle/candidate_sources.py` already pins source manifests, separates links from retained position evidence, associates roster identities, detects full-name/contest collisions and reports coverage gaps. Reuse those invariants and source-association receipts. Replace its hardcoded mixed-source associations and permissive surname fallback for the primary-only product; the old catalog includes reporting links and third-party judicial surveys and is **not** an approved new source allowlist. Official congressional/state-service gateways remain discovery pointers until the exact records are retained/admitted; the old code correctly labels them unanalyzed/historical rather than current positions.

`claim_bindings.py` supplies exact hash/span facts, explicit comparison scope and “missing coverage is not a position” behavior. The corpus/research/release work supplies scope checks, same-request reads, version bindings and withheld outcomes. Retain those independently of AWS/Strands. The ballot-intake contract supplies bounded extraction and honest unverified/OCR states; it does not certify a new candidate filing or transcript. Existing language/voice/currentness and reset tests provide useful regressions; they do not establish new candidate/transcription coverage, Spanish release or a human-heard journey.

## Agreed bounded hybrid trial

The owner agreed to trial the managed Agents API for **one asynchronous candidate evidence-bundle job**, while retaining application-owned Live/Decisions/Responses conversation control. This is an experiment, not a wholesale harness rewrite or a declaration that Agents API is best. Do not introduce the Agents SDK and API together or a researcher/debater/judge swarm. Keep canonical jobs/effects, corpus versions, rights/identity admission and publication gates outside the managed session. Sandbox expiry is not artifact durability; recovery is not exactly-once execution. Record side effects before any retry.

Verify current account eligibility, endpoint/model pricing and retention before that trial. Use only public, rights-admitted filing fields, an attributed official campaign statement, and a permitted original transcript; keep an unavailable transcript visibly missing instead of fabricating it. Managed Agents sessions persist until deletion and are not ZDR eligible; no personal voter data belongs there. Prefer no sandbox when supplied text/manifest extraction suffices. The SDK remains an alternative if the bounded trial exposes control, retention or integration problems; generic SDK Realtime support is not proof of native GPT-Live support. No model can override a deterministic rights/admission hold.

## Incremental acceptance, before costly expansion

1. Parent approves this source policy and selects one authority, one race/cycle and a small explicit candidate set. Inventory available original filings/records/debate assets, rights and gaps read-only. No nationwide promise.
2. Build metadata/identity/version fixtures: same-name candidates, duplicate URLs/bytes, revised/withdrawn filings, edited clips, missing speaker identity, missing ASR confidence and correction-driven invalidation. Wrong candidate or ballot membership must never release.
3. Ingest a tiny bounded set of already-approved primary text documents. Demonstrate exact-page citations, incremental refresh, deduplication, invalidation and coverage reporting before any audio spend.
4. If needed, reserve one short public debate segment for transcription, with explicit model, duration, per-minute price, language and review criteria. Human-check candidate identity and every released quotation/number. No bulk transcription is authorized by this plan.
5. Evaluate the same factual/unsupported/comparison/injection cases across deterministic and constrained generative variants, then checked audio variants. Record actual failures and denominators, source/identity/citation errors, stale generation/audio escapes, calibration and stage costs. Report p50/p95 only for actual samples large enough to describe; no accuracy percentages from authored fixture counts.
6. Before human trials, get named-device consent. Keep all generated audio in a controlled buffer until complete transcript/current-source/request checks pass; commentary can paraphrase and holding a tool result does not stop spontaneous speech. A pause is not complete-answer proof. Hardware Stop/Erase must clear queued audio and reject late approval. No speaker or microphone activation, Pi change, public deployment or expanded credential scope follows from this plan.

Suggested latency targets (not vendor promises or current results) are ≤3s p95 cached ordinary approved audio and ≤250ms interruption silence. Revise using measured quality/latency tradeoffs rather than weakening source or playback checks. The shared authorized $200 testing ceiling is a maximum; reserve in-flight uncertainty across workers, including Live silence/wait duration and backend usage. No bulk ingestion estimate is claimed until source volume/duration and retention permissions are known.

Official capability references: [voice architectures](https://developers.openai.com/api/docs/guides/voice-agents), [native Live/Decisions](https://developers.openai.com/api/docs/guides/decisions-voice), [Live migration guardrails](https://developers.openai.com/api/docs/guides/live-migration), [speech buffering](https://developers.openai.com/api/docs/guides/voice-server-controls#check-speech-before-playback), [data controls](https://developers.openai.com/api/docs/guides/your-data), [evaluation guidance](https://developers.openai.com/api/docs/guides/evaluation-best-practices). Source admission/scaling/latency targets above are product design, not documented OpenAI guarantees.

## Current execution status — 2026-10-24

The earlier user-approved managed Agents trial is **deferred**, not executed.
Its caller-set dollar ceiling remains unverified; see AGENTS-BUDGET-REVIEW.md.
Continue bounded Responses/application-owned extraction and product integration
without claiming an Agents comparison. No bulk ingestion is authorized by this
status update.
