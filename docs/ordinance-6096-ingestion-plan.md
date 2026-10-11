# Ordinance 6096: bounded ingestion review

This is a source-ingestion plan, not new runtime evidence, legal interpretation, or approval to release new answers. The existing `combat-6096` OCR source stays `unverified_ocr`; its source-wide quality flag must not be elevated.

Core read the verification packet, independently calculated the retained PDF hash, checked all eight selected-transcript offsets, and inspected all five rendered pages. The controlled original is the five-page, 466,739-byte adopted attachment, SHA256 `5fa4474560da047207bfd7c7033de0d0a1febb20d6e92cc6447982ca71a1afde`. Packet JSON SHA256 is `ad8c7fe44fd934217615cd7c931f824e005f104657900b359e0fb47f67e316b2`. All eight extracted spans equal their half-open Unicode offsets in `verified-selected-clauses.txt`; every packet span still says `runtime_release_approved:false`. Fresh attachment-byte matching was not established. The selected transcription joins visual line breaks and normalizes repeated spaces, so it must be labelled a manual selected reading copy rather than exact original PDF typography.

The [verification packet](/Users/danielgreen/Documents/Codex/2026-10-10/task-7/combat-verification-2026-10-11/COMBAT-source-verification-packet.md) remains outside the Git repository with its unchanged original, rendered images, status records and transcript. No original or packet was modified or copied into the runtime archive by this review.

## Smallest safe future import

Create a distinct, explicitly partial source such as `combat-6096-selected-v1`, backed by the same original PDF pin and a separately hashed UTF-8 manual reading copy containing only the eight reviewed passages. Preserve `role:adopted_proposal`, issuer Jackson County Legislature, countywide Jackson County/MO scope and November 3, 2026 context. It is not evidence that the proposed continuation has been approved by voters or has become the complete current tax code. Keep the original unverified OCR source separate; never use selected-span approval to validate its unreviewed remainder.

Construct each chunk directly from the packet's approved start/end rather than re-splitting generic OCR paragraphs. Bind the chunk hash, selected-reading-copy hash, original PDF hash, PDF page, section/locator, transcription method and reviewer-locator box. The normalized image boxes are inspection aids, not machine-extracted character positions. Offsets are Unicode code points in the selected reading copy, not PDF byte offsets or raw OCR offsets. Do not put editorial labels, signature guesses, or the ordinance's statements about success into factual claims.

Initially permit only exact attributed source inspection through legal-reference retrieval. The current finite COMBAT answer contract remains rate/duration plus an explicit prediction refusal. Any additional explanatory form needs its own source-bound claim contract, whole-condition checks, review/display tests and separately authorized live validation before public release. Neither embedding ranking nor Decisions acceptance supplies legal entailment.

## Conditions that must travel with an explanation

Keep the complete page 3 ballot question together with its separate-trust-fund sentence. Rate/duration statements describe a proposed continuation conditional on voter approval. The page 3 Section 4 April 1, 2027 through March 31, 2037 dates are conditional collection-extension dates. The page 5 immediate effectiveness on executive signature concerns the ordinance; it must not be substituted for the tax collection dates. The scan distinguishes June 22 legislative passage from June 23 executive approval.

Section 2 refers to Chapter 93 administration and expressly permits a portion of proceeds for election-authority costs. Any administration/purpose explanation must preserve that exception. The March 31, 2027 expiry is an attributed recital in this adopted document, not proof of an exhaustive current-law amendment search. Prior Ordinance 4881/2016 authorization is historical context, not a current ballot or independently verified full text. An election-board notification directive does not prove notification actually occurred.

The Chapter 93 PDF linked from the official index is a December 11, 2018 edition; no retained byte hash was obtained because raw download failed. Keep its web-reader excerpts as separately labelled context until a controlled original and amendment currency can be verified. Ordinance 6120's withdrawn proposal must not replace 6096 or be presented as enacted law. Never splice the code's percentage wording into the ballot's printed cent wording. Revenue, household forecasts, crime effectiveness, recommendations and complete legal compliance stay unsupported.

## Required import checks

Before importing: validate original/transcript/packet pins; all eight spans, page/section references and duplicate IDs; ensure other OCR bytes cannot become selected chunks. Test source role, date/version/jurisdiction mismatches, voter-approval condition, trust-fund sentence, election-cost exception, both distinct effective dates and withdrawn-proposal exclusion. A changed original, transcript, reviewer locator or passage must fail the import. Build vector coverage only for explicitly approved public source strings; prepare strict completeness before any inference. No cloud upload or model test is part of this plan.
