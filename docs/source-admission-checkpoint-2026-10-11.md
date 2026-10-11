# Source admission and integration checkpoint

October 11, 2026. Local implementation and offline proof; no paid API calls,
credential changes, capture, playback, deployment or publication.

## Missouri SOS: admitted to an opt-in private index

The reviewed packet contains five retained originals, twelve claim groups and
fifteen exact Unicode evidence spans. `strands_quality/voting_procedure.py`
validates the immutable packet, original and extraction hashes, source URLs,
scope, PDF page offsets and publication-date precision. The local originals are
in ignored `.local/sources/missouri-voting-procedure`; the original staging pack
is unchanged. `scripts/admit_voting_procedure.py` installs only verified files,
refuses conflicting existing originals and constructs the real FTS5 index.

```sh
.venv/bin/python scripts/admit_voting_procedure.py --archive .local/sources/missouri-voting-procedure
```

Core/private research can explicitly call
`load_verified_corpus(corpus, voting_procedure_archive=archive)` and use the new
`voting_procedure` purpose in the existing Strands plan/search/acquire/read
workflow. Default application loading remains unchanged; this is not an enabled
public voting-procedure endpoint. Actual independent live release remains unrun.

The evidence role is separate from ballot facts, current law, legal references,
predictions and candidate claims. Scope, election, versions and snapshot date
filter retrieval. Hours inspection always includes the closing-line exception.
PDF extraction layout remains unverified and cannot support released citations.
Undated web publication dates stay null; month-only PDF revisions stay month-only.
No visitor eligibility, registration or polling location is inferred or collected.

Primary sources: [SOS How to Vote](https://www.sos.mo.gov/elections/goVoteMissouri/howtovote),
[Voter ID](https://www.sos.mo.gov/voterid),
[Election Calendar](https://www.sos.mo.gov/elections/calendar). These were read
again during integration; this does not adjudicate all current operational rules,
calendar headers or interleaved PDF exceptions for public release.

Twelve new regression tests cover actual originals, exact spans, changed or
missing files, late original drift, private index search, wrong roles/scope/date/
versions, publication precision, hours qualification and PDF citation holds.

## Chapter 93: full retained original, current-law gap remains

Ordinary public download from the official County Code link succeeded: 48,655
bytes, three pages, SHA256
`b437d1e21fdd3fa83e0403fda45e9d781a8e891e9d9d5601a2041cb4bcd83596`.
All three page images were inspected against native extracted text. Extraction
SHA256 is `575830242331f0ac78797ddc53b862cdc2fbc95654cb06d9c69cd8179bb9cc2d`.

`strands_quality/chapter93.py` admits all three pages as `historical_law`, with
an explicit printed-2018/currency-unverified label. Invoke
`load_verified_corpus(corpus, county_code_archive=archive)` with ignored
`.local/sources/county-code-chapter-93` for private legal-reference retrieval.
It does not satisfy current-law, ballot-fact or prediction purposes and does not
replace the eight selected adopted-proposal passages or the original OCR source.
Four tests cover complete page boundaries, exact text, changed originals and
exclusion from current-law/ballot release.

The [official County Code index](https://www.jacksongov.org/Government/County-Code)
links the document but advises verifying accuracy with the County Clerk before
reliance. Its printed edition is December 11, 2018 and contains later effective-
date annotations. Subsequent amendments and legal currency are not adjudicated;
no clerk contact or personal inquiry occurred. The earlier raw-download blocker
is resolved; the current-law completeness gate is still open.

## Broader source/release work remains

The roster still contains 62 candidates plus eleven judicial-retention subjects.
Prepared attributable Pollard/Fields answers cover two shared questionnaire
topics. Other candidate links are discovery pointers, not retained position
evidence. Complete candidate/current-law coverage and broader generated release
must stay pending until original retention, exact scoped claim mappings,
condition coverage and independent release validation are complete.

## Managed guardrail adapter: imported, inactive

`open_oracle/aws_guardrails.py` and the reviewed configuration proposal are now
available for explicit future use. Thirty-four offline service-contract tests
pass, including full coverage, immutable ARN/version scope, missing policies,
interventions, cancellation, changed-content reuse, metadata privacy, no retry
and authorization errors. Reservation failures return a fixed unavailable result
without echoing visitor content or private accounting errors.

The adapter is not connected to the server and created or called no AWS resource.
A reviewed immutable resource/version/configuration, permitted principal,
bounded reservation and actual service acceptance are still required before
activation. Decisions and deterministic release contracts remain mandatory.
An AWS result alone cannot approve civic factual meaning.
[Primary ApplyGuardrail API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_ApplyGuardrail.html).

## Accessibility and verification

See [the scoped kiosk audit](kiosk-accessibility-checkpoint-2026-10-11.md).
The first complete canonical rerun after SOS admission ran 559 tests: 555 passed,
four optional skips. The earlier sandbox run was blocked on temporary HTTP
fixture sockets; it was not an application-quality failure. The permitted rerun
passed. Later adapter/Chapter 93 tests separately passed 34 and four cases.
Final combined rerun: 597 tests ran, 593 passed and four optional tests skipped.
The kiosk rerun has twelve states with zero automated violations and no root
incomplete checks after the semantic group-role fix. Copilot contrast still
requires manual verification. README now has three Mermaid diagrams; all 77
relative references resolve. Raw outputs/screenshots are retained in the isolated
task folder `source-integration`, not committed as visitor or public content.

Physical microphone/speaker, screen reader, continuous two-turn/Stop/Resume,
wave/Pi, final pitch approval, recording and submission remain separate human/
device or deployment acceptance. No completed-status claim follows from imports.
