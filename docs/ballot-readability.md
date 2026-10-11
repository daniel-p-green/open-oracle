# Ballot readability tool

`open_oracle.readability` provides a deterministic English FRE/FKGL estimator and `build_readability_tool()` returns a real Strands `@tool`. It requires `cmudict==1.1.1`, no provider, model call, credential, or Readable.com account. Verified with installed `strands-agents==1.59.0`.

The output preserves raw text, scored text, hashes, cleaning operations, provenance, per-token syllable counts, warnings, formulas and counting conventions. `exact_ballotpedia_score` is always false and `factual_fidelity_status` is always `not_evaluated`. Empty input produces null scores. Unsupported language produces null scores. Text is bounded to 20,000 characters.

## Source methodology

[Ballotpedia's 2026 page](https://ballotpedia.org/Ballot_measure_readability_scores,_2026) was extracted through Exa on October 11, 2026 after direct access returned a robot check/403. It describes separate title/question and summary scoring with Flesch Reading Ease and Flesch-Kincaid Grade Level using Readable.com. Its retrieved score section had no 2026 measure rows. Formula results estimate surface difficulty and cannot measure idea complexity or demonstrated comprehension. The extraction does not independently establish a live page revision or Readable.com's tokenizer, syllable dictionary, numeric expansion, sentence rules, rounding, or exact scored strings.

[Readable's formula documentation](https://readable.com/readability/flesch-reading-ease-flesch-kincaid-grade-level/) and its two linked formula images were read and visually verified. For W words, S sentences, and Y syllables:

```text
FRE  = 206.835 - 1.015 * W/S - 84.6 * Y/W
FKGL = 0.39 * W/S + 11.8 * Y/W - 15.59
```

The tool uses these coefficients; its counting rules are our explicit implementation choices. It does not reconstruct Ballotpedia or Readable.com's proprietary counting behavior. Historical Ballotpedia tables in `research/HackMidwest2026_research/Readability-Reference` remain secondary published scores with separately documented text-version gaps. They are not calibration ground truth for this sample.

## Implementation choices

- Collapse whitespace, replace curly apostrophes with ASCII, and replace bullet glyphs with spaces. Preserve the raw input; no OCR correction, sentence rewrite, number expansion, legal-clause deletion, or spelling normalization.
- Words match ASCII alphabetic sequences with internal apostrophes, or written numerals with decimal/thousands punctuation and optional percent signs. Hyphens split into separate words. Dotted initials/abbreviations tokenize alphabetic components. A trailing possessive apostrophe has no extra token.
- Sentence endings are periods, question marks and exclamation marks. A finite list of abbreviations (`U.S.`, `e.g.`, `i.e.`, `Mr.`, `Mrs.`, `Ms.`, `Dr.`, `Jr.`, `Sr.`, `No.`), capital initials before a capital letter, and decimal periods are protected. Semicolons and list bullets are not sentence endings. Any remaining fragment counts as one sentence. Sentence segmentation is heuristic; abbreviations outside the list can change counts.
- Syllables use the first pronunciation in pinned CMUdict 1.1.1. Unknown words use vowel-group counts, subtract a terminal silent e except consonant+le, with a minimum of one. Numerals have one nominal syllable; warnings expose this choice. The KCEB question fixture has one unknown word, `warranto`, counted as three by the fallback. Every token and its counting basis is returned.
- Round scores to four decimal places; preserve negative FRE/grade values and values over 100. High grade estimates are not literal required educational credentials. There is no derived ballot-wide average, score cutoff, pass/fail, ranking of policy merit, or inference about political bias.
- Under 100 words triggers a sensitivity warning. This is an application rule, not a Ballotpedia minimum. Caller-declared English is required; non-ASCII letters are unsupported. No language detector or validated non-English formula is provided. Unaccented non-English text incorrectly labeled English cannot be reliably detected.

## Strands integration

```python
from open_oracle.readability import build_readability_tool

readability_tool = build_readability_tool(corpus, scope=application_scope)
# Add readability_tool to an Agent's tools only for an explicit readability request.
result = readability_tool(evidence_id="combat:jceb-sample", span="question")
```

The corpus path reads only applicable current-snapshot measure evidence, binds its title and provenance from the application, rejects candidate evidence and replacement text, and selects the question body or separate `fiscal_summary`. The original full evidence is returned alongside the selected span, with selection offsets. COMBAT's follow-on trust-fund sentence remains inside its complete policy body. Scope is injected when constructing the tool, not chosen by the model.

The supplied-text path scores the exact supplied span, with provenance explicitly labeled `caller_asserted_unverified`. It does not fetch, authenticate, or verify URLs. A model-generated passage must not be relabeled official simply by adding a source URL. The application must choose one identified question or summary, not feed a whole PDF or roster. Tool descriptions cannot enforce semantic segmentation for arbitrary supplied text.

The current selector adds a restricted `test_ballot_readability(evidence_id)` tool only for an explicit readability/Flesch/reading-level request about a measure. Its model-facing schema exposes no replacement text, source URL, language, scope or span selection. The application owns the span and requires the selected passage to have been read in this request. Successful live tool selection requires a readability result before evidence release. Ordinary questions retain resolve/search/read and their existing five-call ceiling. Exact-source mode invokes the actual decorated tool directly with no model inference. The HTTP/CLI response exposes `readability` metadata; the existing UI and speech text remain unchanged. Keep readable wording and factual fidelity as separate checks. No score improvement should release a rewrite until legal conditions, exceptions, actors, dates, amounts and causal limits have survived independent fidelity review. Retain the original and do not optimize a readability score by deleting conditions. This patch supplies no generated rewrite or fidelity approval.

## Reproduce the official KCEB run

The public [KCEB sample page](https://kceb.org/elections/ballot/) linked the September 14 revision of the November 3, 2026 sample, subject to change. Its [Drive PDF](https://drive.google.com/file/d/1K9yPQmPpIB1g9qoErahvNjTGhrBRi9A2/view?usp=sharing) was downloaded on October 11 and matched both existing project copies:

```text
SHA-256: 92cda731c864b5a84062322a32f743597bcace6f986af4c0e2bfe55c7405dc62
457535 bytes; 8 pages; policy measures on pages 7–8
```

```sh
PYTHONPATH=. python scripts/test_kceb_readability.py /path/to/official.pdf /path/to/output
python -m unittest discover -s tests -p 'test_readability.py' -v
```

Poppler `pdftotext` 26.10.0 extracted explicit regions. Both measure pages were rendered and visually inspected against all six policy bodies; flattened whole-page reading order is unsuitable. The extraction script aborts on a different PDF hash. It selects complete question bodies and separately printed fiscal paragraphs, excluding headings, authorship, choices and instructions. Judicial retentions and candidate rosters are excluded from this policy-measure run, not scored as an aggregate. The script writes raw region evidence, raw input spans, JSON with audits, and CSV metrics.

No parallel vetted plain-language text was supplied, so no original/rewrite comparison ran. No personal voter lookup or eligibility determination was performed. Live page state and later revisions can change; this run describes the hash-pinned public sample only.
