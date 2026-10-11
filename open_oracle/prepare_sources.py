"""Explicit source preparation command. Never invoked by the web app or tests."""
from datetime import datetime, timezone
import json
from urllib.request import Request, urlopen
from .demo_sources import ROOT, URL, PASSAGE_HASHES, digest, extract


def main():
    raw = urlopen(Request(URL, headers={"User-Agent": "OpenOracleSourceReview/0.1"}), timeout=30).read()
    entries = extract(raw)
    if any(PASSAGE_HASHES.get(e["topic"] + ":" + e["candidate_name"]) != e["passage_sha256"] for e in entries):
        raise ValueError("Publisher answers differ from the inspected version; review before replacing the archive")
    ROOT.mkdir(parents=True, exist_ok=True)
    # Validate before replacing either local file. Failure leaves the prior archive usable.
    (ROOT / "beacon-atlarge-2026-09-22.html").write_bytes(raw)
    (ROOT / "beacon-atlarge.json").write_text(json.dumps({"url": URL, "archive_sha256": digest(raw),
        "retrieved_date": datetime.now(timezone.utc).date().isoformat(), "entries": entries}, ensure_ascii=False, indent=2))
    print(f"Prepared {len(entries)} complete attributed answers across two shared questions. No model calls.")


if __name__ == "__main__":
    main()
