"""Deterministic English ballot surface-readability estimates, never a fidelity gate."""
from __future__ import annotations

from functools import lru_cache
import hashlib
import importlib.metadata
import re

METHOD_VERSION = "open-oracle-flesch-en-v1"
MAX_CHARS = 20000
READABILITY_REQUEST = re.compile(r"\breadability\b|\bflesch\b|\bfkgl\b|\breading (?:grade|level)\b|\bhow (?:hard|difficult) .*\bread\b", re.I)


def requested_span(question: str) -> str | None:
    """Only explicit surface-readability requests add the diagnostic tool."""
    if not READABILITY_REQUEST.search(question):
        return None
    return "fiscal_summary" if re.search(r"\bfiscal\b", question, re.I) else "question"
WORD = re.compile(r"\d+(?:[,.]\d+)*%?|[A-Za-z]+(?:['’][A-Za-z]+)?")
ABBREVIATION = re.compile(r"\b(?:U\.S\.|e\.g\.|i\.e\.|Mr\.|Mrs\.|Ms\.|Dr\.|Jr\.|Sr\.|No\.)", re.I)


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def clean_text(raw: str) -> tuple[str, list[dict]]:
    """Only typographic cleanup. Never repair OCR, delete clauses, or rewrite."""
    audit = []
    text = raw
    for name, transform in [
        ("curly_apostrophes_to_ascii", lambda s: s.replace("’", "'").replace("‘", "'")),
        ("bullet_glyphs_to_spaces", lambda s: re.sub(r"[●•▪]", " ", s)),
        ("collapse_whitespace", lambda s: " ".join(s.split())),
    ]:
        changed = transform(text)
        if changed != text:
            audit.append({"operation": name, "before_sha256": sha256(text), "after_sha256": sha256(changed)})
        text = changed
    return text, audit


@lru_cache(maxsize=1)
def dictionary() -> dict:
    import cmudict
    if importlib.metadata.version("cmudict") != "1.1.1":
        raise RuntimeError("Readability requires pinned cmudict==1.1.1 for reproducible counts")
    return cmudict.dict()


def syllables(token: str) -> tuple[int, str]:
    if token[0].isdigit():
        return 1, "numeric_placeholder"
    key = token.lower().rstrip("'")
    entries = dictionary().get(key)
    if entries:
        return sum(p[-1:].isdigit() for p in entries[0]), "cmudict_first_pronunciation"
    # Documented fallback: vowel groups, silent terminal e except consonant+le.
    key = re.sub("[^a-z]", "", key)
    count = len(re.findall(r"[aeiouy]+", key))
    if key.endswith("e") and not re.search(r"[^aeiouy]le$", key) and count > 1:
        count -= 1
    return max(1, count), "vowel_group_fallback"


def sentences(text: str) -> list[str]:
    masked = ABBREVIATION.sub(lambda m: m[0].replace(".", "\u2024"), text)
    masked = re.sub(r"\b[A-Z]\.(?=\s+[A-Z])", lambda m: m[0].replace(".", "\u2024"), masked)
    masked = re.sub(r"(?<=\d)\.(?=\d)", "\u2024", masked)
    return [s.strip().replace("\u2024", ".") for s in re.split(r"[.!?]+", masked) if WORD.search(s)]


def formula_scores(words: int, sentence_count: int, syllable_count: int) -> dict:
    if min(words, sentence_count, syllable_count) <= 0:
        raise ValueError("Formula inputs must be positive")
    return {"flesch_reading_ease": round(206.835 - 1.015 * words / sentence_count - 84.6 * syllable_count / words, 4),
            "flesch_kincaid_grade_level": round(0.39 * words / sentence_count + 11.8 * syllable_count / words - 15.59, 4)}


def analyze_readability(text: str, label: str, provenance: dict | None = None,
                        language: str = "en", extraction_method: str = "user_supplied") -> dict:
    """Score exactly one question or separately identified summary; preserve input."""
    if not isinstance(text, str) or not isinstance(label, str):
        raise ValueError("text and label must be strings")
    if len(text) > MAX_CHARS or len(label) > 200:
        raise ValueError("Maximum 20,000 text characters and 200 label characters")
    if not label.strip():
        raise ValueError("Identify the measure and scored text span")
    cleaned, audit = clean_text(text)
    result = {"label": label, "method_version": METHOD_VERSION, "language": language,
              "status": "estimated", "raw_text": text, "raw_text_sha256": sha256(text),
              "scored_text": cleaned, "scored_text_sha256": sha256(cleaned), "cleaning_audit": audit,
              "provenance": dict(provenance or {}), "extraction_method": extraction_method,
              "counts": None, "scores": None, "token_audit": [], "warnings": [],
              "method": {"fre_formula": "206.835 - 1.015*(W/S) - 84.6*(Y/W)",
                         "fkgl_formula": "0.39*(W/S) + 11.8*(Y/W) - 15.59",
                         "variables": "W=words, S=sentences, Y=syllables",
                         "word_policy": "ASCII words with internal apostrophes; hyphens split words; written numerals count once",
                         "sentence_policy": "Periods, question/exclamation marks; common abbreviations, initials, decimals protected; semicolons/bullets do not split; final fragment counts",
                         "syllable_policy": "cmudict==1.1.1 first listed pronunciation; unknown words use vowel-group heuristic; written numerals nominally one syllable",
                         "rounding": "Four decimal places, no clipping; no categorical grade bands or pass/fail"},
              "exact_ballotpedia_score": False, "factual_fidelity_status": "not_evaluated",
              "limitations": ["Surface-language estimate; does not measure comprehension, factual fidelity, legal effect, or political bias.",
                              "Does not reproduce Readable.com tokenization or Ballotpedia scores. No pass/fail or voting recommendation."]}
    if language not in ("en", "en-US", "en-GB") or any(c.isalpha() and not c.isascii() for c in cleaned):
        result.update(status="unsupported_language")
        result["warnings"].append("Only caller-declared English with ASCII letters is supported; no language detection or validated translation scoring.")
        return result
    tokens = WORD.findall(cleaned)
    if not tokens:
        result["status"] = "empty"
        result["warnings"].append("No words; formulas undefined. Scores are null, not zero.")
        return result
    split_sentences = sentences(cleaned)
    token_audit = [{"token": t, "syllables": syllables(t)[0], "basis": syllables(t)[1]} for t in tokens]
    result["token_audit"] = token_audit
    result["counts"] = {"words": len(tokens), "sentences": len(split_sentences),
                        "syllables": sum(t["syllables"] for t in token_audit),
                        "words_per_sentence": round(len(tokens) / len(split_sentences), 4),
                        "sentence_word_counts": [len(WORD.findall(s)) for s in split_sentences]}
    result["scores"] = formula_scores(len(tokens), len(split_sentences), result["counts"]["syllables"])
    if len(tokens) < 100:
        result["warnings"].append("short_text_under_100_words: estimates sensitive to tokenization; 100 is an application warning, not a Ballotpedia scoring cutoff.")
    if any(t["basis"] == "numeric_placeholder" for t in token_audit):
        result["warnings"].append("numbers: each written numeral is one word and one nominal syllable; not expanded into spoken English.")
    if any(t["basis"] == "vowel_group_fallback" for t in token_audit):
        result["warnings"].append("out_of_dictionary_words: inspect token_audit for heuristic syllable counts.")
    if "ocr" in extraction_method.lower() or "\ufffd" in text or re.search(r"[a-z][A-Z]", text):
        result["warnings"].append("extraction_review_required: OCR/replacement glyph or joined-word pattern; text has not been repaired.")
    if re.search(r"\b[A-Z]{2,}\b|\b[A-Za-z]\.", cleaned):
        result["warnings"].append("abbreviations_or_uppercase: known forms/initials protected for sentence splitting; word syllables use dictionary then fallback, not spelled-out letters.")
    if not re.search(r"[.!?][\s\"'’”)]*$", cleaned):
        result["warnings"].append("unterminated_fragment_counted_as_sentence")
    return result


def measure_span(raw: str, span: str) -> tuple[str, int, int]:
    """Select a complete policy body, retaining follow-on legal conditions after '?' ."""
    if span not in ("question", "fiscal_summary"):
        raise ValueError("span must be question or fiscal_summary")
    start_match = re.search(r"\b(?:Shall|Do)\b", raw)
    if not start_match:
        raise ValueError("No policy-question boundary found; manually identify the span")
    start = start_match.start()
    end_match = re.search(r"\bYES\s+NO\b", raw[start:])
    end = start + end_match.start() if end_match else len(raw)
    fiscal = re.search(r"\bState\s+(?:and\s+local\s+)?government(?:al)?\s+entities", raw[start:end])
    if span == "fiscal_summary":
        if not fiscal:
            raise ValueError("No separate fiscal-summary span")
        start += fiscal.start()
    elif fiscal:
        end = start + fiscal.start()
    return raw[start:end], start, end


def build_readability_tool(corpus=None, scope: dict | None = None):
    """Create a real installed-SDK tool without constructing a paid model/provider."""
    from strands import tool
    bound_scope = dict(scope or {})

    @tool
    def test_ballot_readability(text: str = "", label: str = "", evidence_id: str = "",
                               language: str = "en", source_url: str = "", page: int = 0,
                               extraction_method: str = "user_supplied", span: str = "question") -> dict:
        """Estimate English FRE/FKGL for one ballot question or summary, retaining original wording.

        Args:
            text: Exact user-supplied text; never score a candidate roster or entire ballot.
            label: Measure name and question/summary span label.
            evidence_id: Optional existing corpus evidence ID; app binds original text and provenance.
            language: Explicit language; only English scoring validated.
            source_url: Caller-asserted public source URL for supplied text; not verified by this tool.
            page: Caller-asserted one-based source page, or zero if unknown.
            extraction_method: How text was obtained; OCR input triggers a review warning.
            span: For corpus evidence, select question or separate fiscal_summary. For supplied text, a span label only.
        """
        if evidence_id:
            if corpus is None or text:
                raise ValueError("Evidence ID requires a corpus and cannot accompany replacement text")
            evidence = corpus.read(evidence_id, bound_scope)
            if not evidence or corpus.contests[evidence["contest_id"]]["kind"] != "measure":
                raise ValueError("No applicable measure evidence")
            original = evidence["text"]
            scored, start, end = measure_span(original, span)
            provenance = {k: v for k, v in evidence.items() if k != "text"}
            provenance.update(provenance_status="application_bound_snapshot", span=span,
                              span_start_offset=start, span_end_offset_exclusive=end,
                              original_evidence_text_sha256=sha256(original))
            result = analyze_readability(scored, corpus.contests[evidence["contest_id"]]["title"] + " — " + span,
                                         provenance, language, evidence.get("extraction", "retained_reading_copy"))
            result["original_evidence_text"] = original
            return result
        if span not in ("question", "fiscal_summary"):
            raise ValueError("span must be question or fiscal_summary")
        if page < 0:
            raise ValueError("page must be nonnegative")
        return analyze_readability(text, label, {"url": source_url, "page": page or None,
                                                "provenance_status": "caller_asserted_unverified"},
                                   language, extraction_method)

    return test_ballot_readability


def diagnostic_answer(readability: dict) -> str | None:
    """Finite diagnostic prose from verified tool results; never election-effect claims."""
    if not isinstance(readability, dict):
        return None
    reports = readability.get("reports", [])
    if not isinstance(reports, list) or len(reports) != 1 or not isinstance(reports[0], dict) or reports[0].get("status") != "estimated":
        return None
    try:
        scores = reports[0]["scores"]
        ease = f"{scores['flesch_reading_ease']:.2f}"
        grade = f"{scores['flesch_kincaid_grade_level']:.2f}"
    except (KeyError, TypeError, ValueError):
        return None
    return (f"The wording scores {grade} on a scale based on school reading grades. Higher numbers mean harder wording. "
            f"It scores {ease} on a separate reading-ease scale, where higher numbers mean easier wording. "
            "These scores are estimates from counts of words, sentences and syllables—the parts of words you hear. "
            "They do not tell us whether someone understands the wording or whether it is accurate.")


def verify_diagnostic(response: dict, corpus=None) -> bool:
    """Recompute every report from the exact scoped original, rejecting any changed field."""
    data = response.get("readability")
    if not isinstance(data, dict) or data.get("execution") not in {"strands_tool_direct", "strands_tool_agent"}:
        return False
    reports = data.get("reports", [])
    if len(reports) != 1:
        return False
    try:
        report = reports[0]
        source_id = report['provenance']['id']
        source = next(s for s in response['evidence'] if s['id'] == source_id)
        span = report['provenance']['span']
        if corpus is not None:
            expected = build_readability_tool(corpus, response['scope'])(evidence_id=source_id, span=span)
        else:
            # Reviewer preflight can verify math/binding; core additionally binds the retained corpus.
            scored, start, end = measure_span(source['text'], span)
            provenance = {k:v for k,v in source.items() if k != 'text'}
            provenance.update(provenance_status='application_bound_snapshot', span=span,
                              span_start_offset=start, span_end_offset_exclusive=end,
                              original_evidence_text_sha256=sha256(source['text']))
            expected = analyze_readability(scored, report['label'], provenance, 'en', source.get('extraction','retained_reading_copy'))
            expected['original_evidence_text'] = source['text']
        return report == expected and response['answer'] == diagnostic_answer(data)
    except (KeyError, TypeError, ValueError, StopIteration):
        return False
