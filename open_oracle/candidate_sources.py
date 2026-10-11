"""Bounded candidate source catalog. Links/summaries never become candidate position quotes."""
from __future__ import annotations

import hashlib
import json
import re

from .corpus import ELECTION, normalized, slug

SUMMARY_SHA = "4f5e212213e9d2b9e38051d60736c0975e2f71c976f498a90b1b146b2452720e"
MANIFEST_SHA = "72f7febbafb8a7c1a708eccd5e634581d740cded636577c69b31328707b9fabc"

# Exact roster identities and source associations inspected in candidate-sources.md.
ASSOCIATIONS = {
    "auditor-questionnaire": ["Scott Fitzpatrick", "Quentin Wilson", "Dustin Coffell"],
    "vote411-us-house-4": ["Mark Alford", "Jordan Herrera", "Thomas Holbrook"],
    "beacon-county-executive": ["Alan Rohlfing", "Stacy Lake"],
    "beacon-county-at-large": ["Lance Pollard", "Carla Fields", "Gresia Cabrera", "Donna Peyton", "Susan B. Wilson"],
    "beacon-county-districts": ["Kelly Thompson", "Venessa Huskey", "Scott Qualls", "Phyllis Hernandez", "Lon McDonald", "Byron Townsend", "Dale Carter", "Antoine D. Jennings", "Bill Haley", "Tony Lawson"],
    "independent-senate-8": ["Jon Patterson", "Keri Ingle"],
    "congress-alford": ["Mark Alford"], "congress-cleaver": ["Emanuel Cleaver, II"],
    "senator-brattin": ["Rick Brattin"],
}
JUDGES = {
    "Paul C. Wilson": "paul-wilson", "Lisa White Hardwick": "lisa-white-hardwick",
    "Kenneth R. Garrett, III": "kenneth-garrett", "Patrick C. Edwards": "patrick-edwards",
    "Lauren D. Barrett": "lauren-barrett", "Cory L. Atkins": "cory-atkins",
    "Kevin D. Harrell": "kevin-harrell", "Abbie Rothermich": "abbie-rothermich",
    "R. Travis Willingham": "r-travis-willingham", "Kea S. Bird-Riley": "kea-bird-riley",
    "Mary Frances Weir": "mary-frances-weir",
}
NONRESPONSES = {normalized(n) for n in ("Dustin Coffell", "Scott Qualls")}
NOT_SURVEYED = {normalized(n) for n in ("Susan B. Wilson", "Kelly Thompson", "Venessa Huskey")}


def aliases(name):
    words = [w for w in normalized(name).split() if w not in ("jr", "ii", "iii")]
    shortened = [w for w in words if len(w) > 1]
    return {normalized(name), " ".join(shortened), shortened[0] + " " + shortened[-1]}


class CandidateSources:
    def __init__(self, corpus):
        self.corpus = corpus
        self.root = corpus.pack / "candidate_records"
        self.available = False
        self.sources = {}
        self.people = {}
        for contest in corpus.contests.values():
            if contest["kind"] not in ("candidate", "retention"):
                continue
            names = [c["name"] for c in contest["candidates"]] if contest["kind"] == "candidate" else [contest["title"].split(": ")[-1]]
            for name in names:
                key = normalized(name)
                if key in self.people and self.people[key]["contest_id"] != contest["id"]:
                    raise ValueError("Candidate full-name collision requires explicit identity reconciliation")
                self.people[key] = {"candidate_id": contest["id"] + ":" + slug(name), "name": name,
                                    "contest_id": contest["id"], "aliases": aliases(name), "sources": []}
        summary, manifest = self.root / "candidate-sources.md", self.root / "manifest.json"
        if not summary.exists() or not manifest.exists():
            return
        if hashlib.sha256(summary.read_bytes()).hexdigest() != SUMMARY_SHA or hashlib.sha256(manifest.read_bytes()).hexdigest() != MANIFEST_SHA:
            return
        records = json.loads(manifest.read_text())
        self.sources = {s["id"]: s for s in records}
        for source_id, names in ASSOCIATIONS.items():
            for name in names:
                self.people[normalized(name)]["sources"].append(source_id)
        for name, ident in JUDGES.items():
            for suffix in ("lawyer", "juror"):
                source_id = "judge-2026-" + ident + "-" + suffix
                if source_id in self.sources:
                    self.people[normalized(name)]["sources"].append(source_id)
        self.available = True

    def _document(self, source_id):
        source = self.sources.get(source_id)
        if not self.available or not source or source.get("status") != "downloaded" or not source.get("raw_file", "").endswith(".pdf"):
            return None
        path = self.root / source["raw_file"]
        if path.parent != self.root or not path.exists():
            return None
        body = path.read_bytes()
        return body if hashlib.sha256(body).hexdigest() == source["sha256"] else None

    def original(self, source_id):
        # Only associated current-cycle survey PDFs; no arbitrary raw HTML or archive paths.
        if not source_id.startswith("judge-2026-") or not source_id.endswith(("-lawyer", "-juror")):
            return None
        return self._document(source_id)

    def lookup(self, contest, question, scope):
        if not self.available or not self.corpus.allowed(contest, scope) or scope.get("election_date", ELECTION) != ELECTION:
            return {"people": [], "conflicts": [], "available": False}
        if re.search(r"\b(?:2024|2025)\b", question):
            return {"people": [], "conflicts": [], "available": False}
        query = " " + normalized(question) + " "
        full_hits = [p for p in self.people.values() if any(" " + a + " " in query for a in p["aliases"] if len(a.split()) > 1)]
        conflicts = {p["contest_id"] for p in full_hits if p["contest_id"] != contest["id"]}
        if conflicts:
            return {"people": [], "conflicts": sorted(conflicts | {contest["id"]}), "available": True}
        candidates = [p for p in self.people.values() if p["contest_id"] == contest["id"]]
        selected = full_hits or [p for p in candidates if " " + next(iter(sorted(p["aliases"], key=lambda a: -len(a.split())))).split()[-1] + " " in query]
        selected = selected or candidates
        result = []
        for person in selected:
            key = normalized(person["name"])
            entries = []
            for ident in person["sources"]:
                source = self.sources[ident]
                is_survey = ident.startswith("judge-2026-")
                kind = "third_party_judicial_survey" if is_survey else "official_record_gateway" if source["status"] == "downloaded" else "independent_reporting_link" if ident == "independent-senate-8" else "candidate_statement_link"
                coverage = "retained_original" if is_survey and self._document(ident) else "original_not_retained" if is_survey else "source_gateway_not_analyzed" if kind == "official_record_gateway" else "full_response_not_retained"
                if key in NONRESPONSES and kind == "candidate_statement_link":
                    coverage = "source_specific_nonresponse"
                if key in NOT_SURVEYED and kind == "candidate_statement_link":
                    coverage = "mentioned_not_surveyed"
                entries.append({"source_id": ident, "url": source["url"], "source_class": source["source_class"],
                                "publication_date": source["publication_date"], "retrieved_date": source["retrieved_utc"].split("T")[0],
                                "election_date": ELECTION, "jurisdiction": "Missouri" if contest["scope"] == "statewide" else "Jackson County, Missouri — " + contest["title"], "electoral_scope": contest["scope"], "kind": kind,
                                "coverage": coverage, "candidate_statement_text_available": False,
                                "original_route": "/api/candidate-original/" + ident if coverage == "retained_original" else None,
                                "original_sha256": source.get("sha256") if coverage == "retained_original" else None,
                                "document_period": "2026 review cycle; retrospective professional/juror evaluation" if is_survey else "Missouri Senate state-service gateway; not a federal voting record or current federal policy statement" if ident == "senator-brattin" else "Mixed historical legislative service; not current policy evidence" if kind == "official_record_gateway" else "2026 election source; publication date as recorded above"})
            result.append({"candidate_id": person["candidate_id"], "candidate_name": person["name"], "contest_id": contest["id"],
                           "election_date": ELECTION, "sources": entries, "position_evidence": "not_retained",
                           "gap": "No retained attributable candidate-position answer. Missing coverage is not a position or adverse judgment."})
        return {"people": result, "conflicts": [], "available": True}
