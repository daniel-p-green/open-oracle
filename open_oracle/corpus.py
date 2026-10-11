"""Read-only, snapshot-specific corpus. Original research is never modified."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import unicodedata

ELECTION = "2026-11-03"
SNAPSHOT = "2026-10-10"
JCEB_URL = "https://jcebmo.org/wp-content/uploads/11.03.26-Notice-of-Election-Sample-Ballot-Poster.pdf"
KCEB_URL = "https://drive.google.com/file/d/1K9yPQmPpIB1g9qoErahvNjTGhrBRi9A2/view"
JCEB_HASH = "032814e650dbdbdb0064acb396ead6f51dcd087778240802eb6c30c7a5ef64a2"
KCEB_HASH = "92cda731c864b5a84062322a32f743597bcace6f986af4c0e2bfe55c7405dc62"
JCEB_TEXT_HASH = "279d07d0896232e763c732d42b64e29191e2dcfd628a2b2dcad00cef62302796"
KCEB_TEXT_HASH = "e9ae66327aa21393167b2cee6bcbd58e341e90a2d2d2590a74bd007e905cd7b5"
INVENTORY_HASH = "c968607ee816fcf6b99ff3c098e5eb63400a95c8a2c139c5dffeef575c1d1a14"


def normalized(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).casefold().replace("’", "'")
    return " ".join(re.findall(r"[a-z0-9]+", value))


def slug(value: str) -> str:
    return normalized(value).replace(" ", "-")


MEASURES = [
    ("amendment-3", "Missouri Amendment 3", "CONSTITUTIONAL AMENDMENT NO. 3", "statewide", None, ["amendment 3"]),
    ("amendment-6", "Missouri Amendment 6", "CONSTITUTIONAL AMENDMENT NO. 6", "statewide", None, ["amendment 6"]),
    ("amendment-7", "Missouri Amendment 7", "CONSTITUTIONAL AMENDMENT NO. 7", "statewide", None, ["amendment 7", "amendment seven", "show me prosperity fund", "prosperity fund"]),
    ("amendment-8", "Missouri Amendment 8", "CONSTITUTIONAL AMENDMENT NO. 8", "statewide", None, ["amendment 8"]),
    ("proposition-a", "Missouri Proposition A", "PROPOSITION A", "statewide", None, ["proposition a", "prop a"]),
    ("combat", "Jackson County Question 1 — COMBAT", "QUESTION # 1", "countywide", None, ["combat", "county question 1", "anti crime sales tax"]),
    ("blue-springs", "Blue Springs use-tax question", "CITY OF BLUE SPRINGS, MO", "municipal", "Blue Springs", ["blue springs", "use tax"]),
    ("independence-bonds", "Independence historic-buildings bond question", "CITY OF INDEPENDENCE, MO", "municipal", "Independence", ["independence", "historic buildings", "bond question"]),
    ("lees-summit", "Lee's Summit waste-collection question", "CITY OF LEE’S SUMMIT, MO", "municipal", "Lee's Summit", ["lee s summit", "lees summit", "solid waste", "waste collection"]),
    ("sni-valley", "Sni Valley Fire Protection District sales-tax question", "SNI VALLEY FIRE", "district", "Sni Valley Fire Protection District", ["sni valley", "fire protection district"]),
]


class Corpus:
    def __init__(self, research: Path | None = None):
        root = Path(__file__).resolve().parents[1]
        self.research = research or Path(os.environ.get("OPEN_ORACLE_RESEARCH", root / "research/HackMidwest2026_research"))
        self.pack = self.research / "OpenOracle-JacksonCounty-2026-Research"
        self.originals = {
            "jceb-sample": self.pack / "jceb/2026-11-03-notice-sample-ballot.pdf",
            "kceb-sample": self.pack / "raw/kceb-sample.pdf",
        }
        self.integrity = {
            key: hashlib.sha256(path.read_bytes()).hexdigest() == expected
            for key, path, expected in [
                ("jceb-sample", self.originals["jceb-sample"], JCEB_HASH),
                ("kceb-sample", self.originals["kceb-sample"], KCEB_HASH),
            ]
        }
        jceb_text = (self.pack / "jceb/2026-11-03-notice-sample-ballot.md").read_bytes()
        kceb_text = (self.pack / "markdown/kceb-sample.md").read_bytes()
        self.integrity["jceb-sample"] &= hashlib.sha256(jceb_text).hexdigest() == JCEB_TEXT_HASH
        self.integrity["kceb-sample"] &= hashlib.sha256(kceb_text).hexdigest() == KCEB_TEXT_HASH
        self.jceb = jceb_text.decode()
        self.kceb = kceb_text.decode()
        if hashlib.sha256((self.pack / "COUNTYWIDE-INVENTORY.md").read_bytes()).hexdigest() != INVENTORY_HASH:
            raise ValueError("Inventory version differs from the inspected snapshot")
        self.contests: dict[str, dict] = {}
        self.evidence: dict[str, dict] = {}
        self._inventory()
        self._passages()
        counts = self.counts()
        if counts != {"contests": 55, "candidates": 62, "retentions": 11, "measures": 10}:
            raise ValueError(f"Snapshot inventory mismatch: {counts}")
        from .candidate_sources import CandidateSources
        self.candidate_sources = CandidateSources(self)
        from .demo_sources import add_to
        add_to(self)
        from .amendment7 import add_to as add_amendment7
        add_amendment7(self)
        from .claim_bindings import fingerprint
        self.contest_fingerprints = {ident: fingerprint({k: v for k, v in contest.items() if k != 'aliases'}) for ident, contest in self.contests.items()}
        self.evidence_fingerprints = {ident: fingerprint(source) for ident, source in self.evidence.items()}

    def _inventory(self):
        text = (self.pack / "COUNTYWIDE-INVENTORY.md").read_text()
        for line in text.splitlines():
            if not line.startswith("| ") or " | " not in line:
                continue
            cells = [x.strip() for x in line.strip("|").split("|")]
            if len(cells) != 2 or cells[0] in {"Office", "Candidate category"} or cells[0].startswith("**"):
                continue
            candidates = []
            for entry in cells[1].split(";"):
                match = re.fullmatch(r"\s*(.+?)\s*\((REP|DEM|LIB)\)\s*", entry)
                if match and "NO CANDIDATE FILED" not in match[1]:
                    candidates.append({"name": match[1], "party": match[2]})
            # The seven KCEB-only rows use prose identifying the party.
            if not candidates and cells[0].startswith(("State Representative", "County Legislator")):
                candidates = [{"name": cells[1], "party": "DEM"}]
            if not candidates:
                continue
            ident = slug(cells[0])
            aliases = [normalized(cells[0])]
            for candidate in candidates:
                aliases.extend([normalized(candidate["name"]), normalized(candidate["name"]).split()[-1]])
            self.contests[ident] = {
                "id": ident, "title": cells[0], "kind": "candidate", "candidates": candidates,
                "aliases": aliases, "scope": "district" if "District" in cells[0] else "countywide" if cells[0] == "Jackson County Executive" else "statewide",
                "required_location": None,
                "coverage": "Printed roster; candidate-position responses are not indexed in this first slice.",
                "applicability": "Printed contest inventory. Authority alone does not assign a personal district or ballot.",
            }
        section = text.split("## Judicial retention: 11 contests", 1)[1].split("## Measures:", 1)[0]
        for match in re.finditer(r"^- (.+?): (.+)$", section, re.M):
            title = match[1] + ": " + match[2]
            ident = "retention-" + slug(match[2])
            self.contests[ident] = {
                "id": ident, "title": title, "kind": "retention", "candidates": [],
                "aliases": [normalized(match[2]), normalized(match[2]).split()[-1]],
                "scope": "countywide", "required_location": None,
                "coverage": "Official retention wording. Performance ratings are not indexed.",
                "applicability": "Retention question in the retained Jackson County samples; no personal-ballot assignment.",
            }
        for ident, title, heading, scope, location, aliases in MEASURES:
            self.contests[ident] = {
                "id": ident, "title": title, "kind": "measure", "candidates": [], "aliases": aliases,
                "scope": scope, "required_location": location, "heading": heading,
                "coverage": "Official question wording and fiscal wording where printed. Full legal-effect analysis is not indexed.",
                "applicability": f"{location} voters only; personal eligibility not established." if location else f"{scope.capitalize()} measure; personal eligibility not established.",
            }

    def _add(self, contest: dict, text: str, source: str, page: int | None, column: int | None = None):
        parent = self.jceb if source == "jceb-sample" else self.kceb
        if not text or text not in parent:
            raise ValueError("Evidence must be an exact span of the retained reading copy")
        ident = contest["id"] + ":" + source
        self.evidence[ident] = {
            "id": ident, "contest_id": contest["id"], "text": text,
            "source_id": source, "url": JCEB_URL if source == "jceb-sample" else KCEB_URL,
            "title": "JCEB November sample ballot" if source == "jceb-sample" else "KCEB November sample ballot",
            "issuer": "Jackson County Election Board" if source == "jceb-sample" else "Kansas City Election Board",
            "source_category": "Official election sample", "election_date": ELECTION,
            "retrieved_date": "2026-10-09", "snapshot_date": SNAPSHOT,
            "version": "Retained November notice" if source == "jceb-sample" else "September 14 revision; subject to change",
            "page": page, "column": column, "start_offset": parent.index(text),
            "sha256": JCEB_HASH if source == "jceb-sample" else KCEB_HASH,
            "status": "current_snapshot" if self.integrity[source] else "conflict",
            "extraction": "Reading-copy text; page visually checked against retained PDF" if source == "jceb-sample" else "Reading-copy text; archived layout caveats; original PDF controls",
            "original_route": "/api/original/" + source,
        }

    def _passages(self):
        for contest in self.contests.values():
            if contest["kind"] == "measure":
                start = self.jceb.index(contest["heading"])
                end_match = re.search(r"\bYES\s+NO\b", self.jceb[start:])
                if not end_match:
                    raise ValueError("Missing measure choices")
                end = start + end_match.end()
                self._add(contest, self.jceb[start:end], "jceb-sample", 1 if start < self.jceb.index("## Page 2") else 2)
            elif contest["kind"] == "retention":
                name = contest["title"].split(": ")[-1]
                for match in re.finditer(r"Shall Judge .*?\bYES\s+NO\b", self.jceb, re.S):
                    if normalized(name) in normalized(match[0]):
                        self._add(contest, match[0], "jceb-sample", 1)
                        break
            else:
                names = [normalized(c["name"]) for c in contest["candidates"]]
                found = False
                # Retain a whole official column for roster context; never reconstruct a ballot from names.
                for match in re.finditer(r"### Column (\d)\n(.*?)(?=\n### Column|\n## Page|\Z)", self.jceb, re.S):
                    if all(name in normalized(match[2]) for name in names):
                        page = 1 if match.start() < self.jceb.index("## Page 2") else 2
                        self._add(contest, match[2], "jceb-sample", page, int(match[1]))
                        found = True
                        break
                if not found:
                    # KCEB-only names may have OCR spacing errors; select the known original page.
                    number = re.search(r"District (\d+)", contest["title"])
                    page = 2 if number and int(number[1]) in (23, 24) else 3
                    match = re.search(rf"## Original PDF page {page}\n(.*?)(?=\n## Original PDF page|\Z)", self.kceb, re.S)
                    self._add(contest, match[1], "kceb-sample", page)

    def counts(self):
        return {"contests": len(self.contests), "candidates": sum(len(c["candidates"]) for c in self.contests.values()),
                "retentions": sum(c["kind"] == "retention" for c in self.contests.values()),
                "measures": sum(c["kind"] == "measure" for c in self.contests.values())}

    def resolve(self, query: str, contest_id: str | None = None) -> list[dict]:
        if contest_id:
            return [self.contests[contest_id]] if contest_id in self.contests else []
        q = " " + normalized(query) + " "
        matches = []
        for contest in self.contests.values():
            score = max((len(alias.split()) for alias in contest["aliases"] if " " + alias + " " in q), default=0)
            if score:
                matches.append((score, contest))
        best = max((score for score, _ in matches), default=0)
        return [contest for score, contest in matches if score == best]

    def allowed(self, contest: dict, scope: dict) -> bool:
        if scope.get("election_date", ELECTION) != ELECTION:
            return False
        location = contest["required_location"]
        if location:
            if scope.get("authority") == "KCEB":
                return False
            key = "district" if contest["scope"] == "district" else "municipality"
            return normalized(scope.get(key, "")) == normalized(location)
        return True

    def search(self, contest_id: str, scope: dict) -> list[dict]:
        contest = self.contests.get(contest_id)
        if not contest or not self.allowed(contest, scope):
            return []
        topic = scope.get("_comparison_topic")
        ballot_source = 'jceb-sample' if scope.get('authority') == 'JCEB' else 'kceb-sample'
        return [e for e in self.evidence.values() if e["contest_id"] == contest_id and e["status"] == "current_snapshot"
                and (contest_id != 'amendment-7' or not self.amendment7_ready
                     or e['source_id'] not in ('jceb-sample', 'kceb-sample') or e['source_id'] == ballot_source)
                and (e.get("topic") == topic if topic else "topic" not in e)]

    def read(self, evidence_id: str, scope: dict) -> dict | None:
        e = self.evidence.get(evidence_id)
        topic = scope.get("_comparison_topic")
        if (e and e["status"] == "current_snapshot" and self.allowed(self.contests[e["contest_id"]], scope)
                and (e['contest_id'] != 'amendment-7' or not self.amendment7_ready
                     or e['source_id'] not in ('jceb-sample', 'kceb-sample')
                     or e['source_id'] == ('jceb-sample' if scope.get('authority') == 'JCEB' else 'kceb-sample'))
                and (e.get("topic") == topic if topic else "topic" not in e)):
            return e
        return None
