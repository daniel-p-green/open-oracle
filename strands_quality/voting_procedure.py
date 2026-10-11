"""Pinned Missouri SOS procedural snapshots for private, source-scoped research.

Indexing is not current-rule adjudication or approval for public prose/speech.
PDF layout remains unverified. Originals and extraction bytes stay outside Git.
"""
from __future__ import annotations
from datetime import datetime
import json
from pathlib import Path
from .research_corpus import Chunk, Source, Registry, Scope, digest

CONTEST_ID = "missouri-voting-procedure"
ADMISSION_SHA256 = "ab1670de3092b92c445d0e9624c17dc775e1d02307916451fc3fcfd18ccb307c"
ELECTION = "2026-11-03"
URLS = {
    "how-to-vote": "https://www.sos.mo.gov/elections/goVoteMissouri/howtovote",
    "voter-id": "https://www.sos.mo.gov/voterid",
    "acceptable-id-pdf": "https://www.sos.mo.gov/CMSImages/ElectionGoVoteMissouri/AcceptableFormsVoterID.pdf",
    "absentee-request-pdf": "https://www.sos.mo.gov/CMSImages/ElectionGoVoteMissouri/AbsenteeBallotRequestForm.pdf",
    "election-calendar": "https://www.sos.mo.gov/elections/calendar",
}

def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate admission key")
        result[key] = value
    return result

def admission(archive: Path) -> dict:
    raw = (Path(archive) / "admission.json").read_bytes()
    if digest(raw) != ADMISSION_SHA256:
        raise ValueError("SOS admission changed from reviewed version")
    data = json.loads(raw.decode("utf-8"), object_pairs_hook=_object)
    if (data["schema"] != "open-oracle-source-admission-v1" or
            data["status"] != "staged_not_indexed" or
            data["requested_election_date"] != ELECTION or
            data["reverify_before_serving"] is not True or
            data["personal_data_collected"] is not False or
            data["personal_eligibility_determined"] is not False or
            data["local_polling_assignment_determined"] is not False):
        raise ValueError("Unsupported procedural admission")
    if len(data["sources"]) != 5 or len(data["claims"]) != 12:
        raise ValueError("Incomplete procedure packet")
    return data

def load_voting_procedure(archive: Path) -> tuple[list[Source], list[Chunk]]:
    """Build direct exact-span chunks only after validating the complete packet.

    archive is application-owned; never accept it as a model/tool argument.
    Missing or changed bytes fail closed. No HTTP or model operation is used.
    """
    archive = Path(archive)
    packet = admission(archive)
    sources, chunks, texts = [], [], {}
    seen = set()
    for entry in packet["sources"]:
        ident = entry["id"]
        if ident in seen or ident not in URLS:
            raise ValueError("Unknown or duplicate procedure source")
        seen.add(ident)
        suffix = ".pdf" if entry["content_type"] == "application/pdf" else ".html"
        if (entry["original_path"] != ident + suffix or
                entry["extracted_path"] != ident + ".txt" or
                entry["requested_url"] != URLS[ident] or entry["final_url"] != URLS[ident] or
                entry["role"] != "official_voting_procedure" or
                entry["jurisdiction"] != "Missouri statewide" or
                entry["indexed"] is not False or entry["release_status"] != "staged_admission_only"):
            raise ValueError("Source identity, role or path differs")
        original_path = archive / entry["original_path"]
        original, extracted = original_path.read_bytes(), (archive / entry["extracted_path"]).read_bytes()
        if digest(original) != entry["raw_sha256"] or digest(extracted) != entry["text_sha256"]:
            raise ValueError("SOS original or extraction changed")
        text = extracted.decode("utf-8")
        texts[ident] = text
        sources.append(Source(
            "sos-procedure-" + ident, "Missouri SOS — " + ident.replace("-", " "),
            entry["final_url"], "Missouri Secretary of State", "official_voting_procedure",
            original_path, entry["raw_sha256"], text, entry["text_sha256"],
            "Retained extraction; exact Unicode offsets. Publication date: " +
            str(entry["publication_date"]) + "; precision: " + str(entry["publication_date_precision"]) +
            ". Undated is not the retrieval date. General guidance only; reverify before serving. " +
            ("PDF layout not adjudicated; citation release held." if suffix == ".pdf" else "Native HTML snapshot."),
            county=None, authority=None, election_date=ELECTION,
            retrieved_date=datetime.fromisoformat(entry["retrieved_at_utc"]).date().isoformat(),
            quality="unverified_layout" if suffix == ".pdf" else "native_html"))
    for claim in packet["claims"]:
        for number, span in enumerate(claim["evidence"]):
            entry = next(s for s in packet["sources"] if s["id"] == span["source_id"])
            start, end = span["start"], span["end"]
            if (type(start) is not int or type(end) is not int or not 0 <= start < end <= len(texts[entry["id"]]) or
                    span["quote"] != texts[entry["id"]][start:end] or
                    span["text_sha256"] != entry["text_sha256"] or span["url"] != entry["final_url"] or
                    span["publication_date"] != entry["publication_date"]):
                raise ValueError("Procedure evidence differs from exact parent span")
            page = span.get("page")
            if page is not None and not any(p["page"] == page and p["start"] <= start < end <= p["end"]
                                          for p in entry["page_offsets"] or []):
                raise ValueError("Procedure page locator differs")
            chunks.append(Chunk(
                CONTEST_ID + ":" + claim["id"] + ":" + str(number),
                "sos-procedure-" + entry["id"], CONTEST_ID, start, end, span["quote"],
                digest(span["quote"].encode("utf-8")), claim["section"], page=page, applicability="statewide"))
    if len(chunks) != 15 or len({c.id for c in chunks}) != 15:
        raise ValueError("Incomplete or duplicate procedural spans")
    return sources, chunks

def inspect_procedure_claim(registry: Registry, archive: Path, claim_id: str, scope: Scope) -> dict:
    """Read a complete attributed claim group, including linked qualifications.

    This is private source inspection, not personal guidance or accepted prose.
    Polling hours always carries the in-line exception. Interleaved PDF evidence
    is visible as unverified layout and cannot support released citations.
    """
    packet = admission(archive)
    claims = {c["id"]: c for c in packet["claims"]}
    if claim_id not in claims:
        raise ValueError("Unknown admitted claim")
    selected = [claim_id] + (["in_line_at_close"] if claim_id == "polling_hours" else [])
    evidence, qualifications = [], []
    for ident in selected:
        qualifications.append(claims[ident]["qualification"])
        for number, _ in enumerate(claims[ident]["evidence"]):
            chunk = registry.chunks[CONTEST_ID + ":" + ident + ":" + str(number)]
            if not registry.eligible(chunk, scope, CONTEST_ID, "voting_procedure"):
                raise ValueError("Procedure scope, version or snapshot date differs")
            evidence.append(registry.read(chunk.id))
    return {"claim_id": claim_id, "evidence": evidence, "qualifications": qualifications,
            "status": "private_source_inspection", "public_release_approved": False,
            "personal_eligibility_determined": False, "local_polling_assignment_determined": False,
            "current_rules_reverified": False, "publication_dates": {
                s["id"]: {"date": s["publication_date"], "precision": s["publication_date_precision"]}
                for s in packet["sources"]}}
