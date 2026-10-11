# Offline structural-control ranking review

The complete three-chunk COMBAT index admitted the ballot's terminal `YES / NO`
option labels into the same semantic answer-candidate set as the substantive
duration and trust-fund paragraphs. The saved positive application trial records
controls first, duration second, trust-fund text third. Its approved paraphrase
has no lexical matches. With no lexical contribution, the current reciprocal-rank
fusion preserves the semantic order. This establishes a content-eligibility
failure. It does not establish why Titan assigned the greatest similarity to the
option labels: the query vector and cosine scores were not retained.

## Proposed bounded change

`research_corpus.py` adds application-owned `Chunk.chunk_type`, defaulting to
`content`. The existing parser marks only a complete terminal uppercase `YES NO`
or `FOR AGAINST` pair (either order, separated by spaces/tabs or a line break) in
a verified ballot-proposal block containing a preceding question. There is no
contest ID, query match, answer keyword, relevance cutoff, or short-text cutoff.
The source role and extraction quality must already qualify. Unknown languages,
ambiguous layouts, inline prose, quoted labels, single labels, legal references
and unverified OCR remain content. A short substantive sentence remains content.
This rule covers 10 JCEB and 6 KCEB terminal blocks across multiple contests.

The source text, offsets, chunk IDs and hashes remain identical. All originals
and control rows remain available through `Registry.acquire`, `Registry.read`
and lexical search. `read` adds `chunk_type` and
`factual_claim_citation_eligible` (also false for unverified extraction); `citation` rejects typed controls before quote
validation. The actual Strands read tool inspects controls without issuing a factual-claim citation span. Even a sufficiently long option-label span cannot support a factual
claim. The application can inspect displayed options, but this patch supplies no
semantic voting-options answer, voting recommendation or inferred consequence.

`semantic_retrieval.py` first validates **every supplied eligible candidate**
against the complete manifest, original, extraction and exact span. Only then
does it rank content chunks. It validates the complete set again after ranking.
Missing control or content entries still cause the same lexical fallback;
stale bindings, altered originals and cancellation still fail. A controls-only
set is validated and returns no semantic results without embedding a query.
The staged S3 adapter uses content binding hashes in its query filter after the
same complete local validation and rejects a returned control result. No partial
index option is introduced. Existing manifests and retained vectors are unchanged;
corpus/adapter implementation hashes already pin the request's policy revision.

Lexical indexing and fusion stay unchanged. Thus explicit lexical option-label
queries can still return inspectable control rows, whose factual citation is
blocked. This policy addresses semantic answer evidence rather than claiming
that all retrieval or ballot-layout interpretation is solved.

## Verified evidence and boundaries

The retained artifact has three 256-dimensional public-document vectors and no
query vector. Recomputed document-to-document cosines are:

| Document pair | Cosine |
| --- | ---: |
| duration / trust-fund paragraph | 0.48526293748216276 |
| duration / option labels | 0.18936995376151983 |
| trust-fund paragraph / option labels | 0.12041458948348353 |

These numbers are not query scores. Offline document self-similarity checks
rank each substantive document first when its own retained vector is used, and
omit controls. This tests cosine math, source binding and candidate partitioning;
it does not test general semantic retrieval quality.

For a fixed query vector, removing a candidate leaves pairwise cosine scores
and relative order of the remaining candidates unchanged. Applying the proposed
partition to the saved query order therefore projects `duration, trust-fund`.
This is an ordinal replay, not a fresh application trial, reconstructed score,
calibrated margin, or evaluated held-out query. The earlier two-chunk proof's
query scores describe that narrower proof only and cannot describe the full
three-chunk application trial.

The new tests cover all retained board layouts, alternate labels and order,
short substantive content, unknown/ambiguous forms, wrong roles/quality,
structural citation rejection, original/lexical inspection, missing control and
content vectors, stale control bindings, cancellation, jurisdiction/date/version
filters, local document vectors and S3 simulations. Other contests and synthetic
layouts are held out from the COMBAT example for the **classification rule**;
they are not held-out semantic query evaluation. Ten new tests plus current
research, release, clarity and adapter/service regressions ran offline: 61 run,
59 pass, two optional native-adapter skips. One existing S3 simulation assertion
must change from all candidate hashes to content hashes; full validation remains
covered independently.

The current 6096 append remains intact: five sources, 107 chunks, including eight
distinct `combat-6096-selected-v1` legal-reference chunks. All eight remain
content, and their adopted-proposal role excludes them from ballot-fact evidence.
The approved-source manifest remains complete (91 records, including controls);
no 6096 embeddings are implied by this classifier change.

AWS recommends logical paragraphs/sections for embedding segmentation and
assigns similarity computation to the vector store. That supports reviewing
source structure but supplies no guarantee that short ballot labels rank poorly.
[Official Titan embedding documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/titan-embedding-models.html).

## Integration and remaining work

Core integration also gates issued citation spans in `research_agent.py`, with a direct actual-SDK tool regression (no inference). Only these three production modules, one existing simulation assertion, the
new offline test file and this document are in the patch. No loader append,
research composer, service factory, runtime, credential, source grammar or
release threshold is changed. Dependencies are unchanged: standard-library
parser/math, existing Strands and botocore simulations. Apply the hunks in core
and rerun its current offline suite; this isolated review does not change core.

No provider calls, cloud storage, ingestion or vector recreation occurred.
Further broad ranking quality or a fresh end-to-end result would require a
separately authorized evaluation. Missing historical query scores cannot be
recovered offline. Unknown layouts intentionally remain content and may still
need reviewed source typing. Release clarity is core's separate work.
