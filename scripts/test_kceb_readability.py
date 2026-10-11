"""Reproduce the six KCEB policy measures from the public, hash-pinned PDF.

Usage: PYTHONPATH=<staging>:<cmudict environment> python scripts/test_kceb_readability.py PDF OUTPUT
Requires Poppler pdftotext; no model, credential, personal lookup, or network call.
"""
from pathlib import Path
import csv
import hashlib
import json
import re
import subprocess
import sys

from open_oracle.readability import analyze_readability, sha256

EXPECTED_HASH = "92cda731c864b5a84062322a32f743597bcace6f986af4c0e2bfe55c7405dc62"
SOURCE_URL = "https://drive.google.com/file/d/1K9yPQmPpIB1g9qoErahvNjTGhrBRi9A2/view?usp=sharing"
REGIONS = [
    ("amendment-3", "Missouri Amendment 3", 7, (0, 0, 280, 792), 0),
    ("amendment-6", "Missouri Amendment 6", 7, (280, 0, 332, 792), 0),
    ("amendment-7", "Missouri Amendment 7", 7, (280, 0, 332, 792), 1),
    ("amendment-8", "Missouri Amendment 8", 8, (0, 0, 290, 360), 0),
    ("proposition-a", "Missouri Proposition A", 8, (290, 0, 322, 360), 0),
    ("combat", "Jackson County Question 1 — COMBAT", 8, (0, 485, 612, 165), 0),
]


def run(pdf: Path, output: Path):
    digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
    if digest != EXPECTED_HASH:
        raise ValueError("PDF differs from inspected September 14 revision; reconcile before scoring")
    output.mkdir(parents=True, exist_ok=True)
    records = []
    fixtures = []
    for ident, label, page, rect, occurrence in REGIONS:
        x, y, width, height = rect
        cmd = ["pdftotext", "-f", str(page), "-l", str(page), "-x", str(x), "-y", str(y),
               "-W", str(width), "-H", str(height), "-layout", str(pdf), "-"]
        region = subprocess.check_output(cmd).decode("utf-8")
        region_path = output / f"{ident}-region.txt"
        region_path.write_text(region)
        starts = list(re.finditer(r"\b(?:Shall|Do)\b", region))
        start = starts[occurrence].start()
        stop_match = re.search(r"\bYES\b", region[start:])
        stop = start + stop_match.start() if stop_match else len(region.rstrip("\f\n "))
        body = region[start:stop]
        fiscal = re.search(r"\bState\s+(?:and\s+local\s+)?government(?:al)?\s+entities", body)
        spans = [("question", start, start + fiscal.start() if fiscal else stop)]
        if fiscal:
            spans.append(("fiscal_summary", start + fiscal.start(), stop))
        for span, begin, end in spans:
            raw = region[begin:end]
            provenance = {"issuer": "Kansas City Election Board", "url": SOURCE_URL,
                          "official_link_page": "https://kceb.org/elections/ballot/", "page": page,
                          "pdf_sha256": digest, "revision": "2026-09-14", "election_date": "2026-11-03",
                          "download_verified_date": "2026-10-11", "region_points_top_left": list(rect),
                          "region_text_file": region_path.name, "region_sha256": sha256(region),
                          "start_offset": begin, "end_offset_exclusive": end,
                          "span_policy": "Question/body and fiscal paragraph separately; headings, authorship, YES/NO and instructions excluded.",
                          "extraction_review": "Pages 7 and 8 rendered and inspected; layout crop avoids column interleaving. No OCR corrections.",
                          "provenance_status": "official_public_pdf_hash_verified"}
            result = analyze_readability(raw, f"{label} — {span}", provenance, extraction_method="poppler_layout_region")
            result.update(measure_id=ident, span=span)
            records.append(result)
            fixtures.append({"measure_id": ident, "span": span, "raw_text": raw, "provenance": provenance})
    report = {"source_pdf_sha256": digest, "records": records, "policy_measures": 6,
              "question_records": 6, "fiscal_summary_records": 5,
              "scope": "KCEB public sample policy measures only; candidate rosters and 11 judicial retention questions excluded.",
              "plain_language_comparison": "not_run_no_vetted_parallel_rewrite", "ballot_average": None}
    (output / "kceb-readability.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    (output / "kceb-input-spans.json").write_text(json.dumps(fixtures, indent=2, ensure_ascii=False) + "\n")
    columns = ["measure_id", "span", "page", "words", "sentences", "syllables", "flesch_reading_ease", "flesch_kincaid_grade_level", "raw_text_sha256", "warning_count"]
    with (output / "kceb-readability.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for r in records:
            writer.writerow({"measure_id": r["measure_id"], "span": r["span"], "page": r["provenance"]["page"],
                             **{k: r["counts"][k] for k in ["words", "sentences", "syllables"]}, **r["scores"],
                             "raw_text_sha256": r["raw_text_sha256"], "warning_count": len(r["warnings"])})
    print(json.dumps([{k: r[k] for k in ["label", "counts", "scores", "warnings"]} for r in records], indent=2))


if __name__ == "__main__":
    run(Path(sys.argv[1]), Path(sys.argv[2]))
