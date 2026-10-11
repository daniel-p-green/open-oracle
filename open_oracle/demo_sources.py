"""Bounded, attributed questionnaire passages; private originals stay outside Git."""
from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

CONTEST = "county-legislator-1st-district-at-large"
URL = "https://thebeaconnews.org/stories/2026/09/22/jackson-county-election-legislature-at-large-pollard-fields-cabrera-peyton/"
PEOPLE = {"Pollard": "LANCE POLLARD", "Fields": "CARLA FIELDS"}
QUESTIONS = {"issues": "If elected, what issues will you make your own?",
             "property": "What would you do to make property taxes more fair?"}
# Pinned after inspecting the publisher's full answers, including list items.
PASSAGE_HASHES = {
    "issues:LANCE POLLARD": "ff1d9b1d32200b644d227b74ced267e3116f81e1f9395324163bcb9c62eaf6f3",
    "issues:CARLA FIELDS": "2b522e93a71b585240ab4a87ebb6699244540533f1868b3f87b8ad37449277ca",
    "property:LANCE POLLARD": "ad37c200a1f881180d62b7646f8f380c2073c481ae636d1c42efc8b0de234811",
    "property:CARLA FIELDS": "0f44f4fdf00a08381e22b339cfd99d91371268d73e5444c9cfd9f48888a0f265",
}
ROOT = Path(__file__).resolve().parents[1] / ".local/sources"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Blocks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks, self.active, self.parts, self.ident = [], None, [], None

    def handle_starttag(self, tag, attrs):
        if tag in ("h2", "p", "li") and self.active is None:
            self.active, self.parts, self.ident = tag, [], dict(attrs).get("id")
        elif tag == "br" and self.active:
            self.parts.append(" ")

    def handle_data(self, data):
        if self.active:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == self.active:
            self.blocks.append((tag, self.ident, " ".join("".join(self.parts).split())))
            self.active = None


def extract(raw: bytes) -> list[dict]:
    parser = Blocks()
    parser.feed(raw.decode("utf-8"))
    sections, topic, person = {}, None, None
    for tag, ident, text in parser.blocks:
        if tag == "h2":
            topic, person = ident if ident in QUESTIONS else None, None
            if topic:
                if text != QUESTIONS[topic] or topic in sections:
                    raise ValueError("Questionnaire section changed")
                sections[topic] = {name: [] for name in PEOPLE}
        elif topic:
            match = re.match(r"^(Pollard|Fields|Cabrera|Peyton):\s*(.*)$", text)
            if match:
                person = match[1]
                if person in PEOPLE and match[2]:
                    sections[topic][person].append(match[2])
            elif person in PEOPLE and tag in ("p", "li"):
                sections[topic][person].append(text)
    if set(sections) != set(QUESTIONS):
        raise ValueError("Missing questionnaire sections")
    entries = []
    for topic in QUESTIONS:
        for name, candidate in PEOPLE.items():
            text = "\n\n".join(sections[topic][name])
            if not text:
                raise ValueError("Missing attributed answer")
            entries.append({"topic": topic, "candidate_name": candidate, "text": text,
                            "passage_sha256": digest(text.encode())})
    return entries


def load(root: Path = ROOT) -> list[dict]:
    try:
        manifest = json.loads((root / "beacon-atlarge.json").read_text())
        raw = (root / "beacon-atlarge-2026-09-22.html").read_bytes()
        entries = extract(raw)
        if manifest["url"] != URL or digest(raw) != manifest["archive_sha256"] or entries != manifest["entries"]:
            return []
        if any(PASSAGE_HASHES.get(e["topic"] + ":" + e["candidate_name"]) != e["passage_sha256"] for e in entries):
            return []
        return [{**e, "question": QUESTIONS[e["topic"]], "retrieved_date": manifest["retrieved_date"],
                 "archive_sha256": manifest["archive_sha256"]} for e in entries]
    except (OSError, ValueError, KeyError, TypeError):
        return []


def requested_topic(question: str) -> str | None:
    """Only offer the two inspected topics; unknown issues must remain source gaps."""
    from .corpus import normalized
    q = normalized(question)
    if re.search(r"\b(combat|crime|abortion|immigration|climate|endors|record|experience|sports|stadium|truman|sales|support|oppose|vote|voting)\b", q):
        return None
    # Generic comparison defaults visibly to the shared priorities question.
    ignored = {"compare", "comparison", "candidate", "candidates", "lance", "pollard", "carla", "fields",
               "and", "or", "s", "the", "of", "a", "an", "their", "what", "are", "do", "does", "would",
               "how", "about", "on", "tell", "me", "show", "explain", "please", "to", "with", "between", "differ", "different", "say",
               "county", "legislature", "legislator", "1st", "first", "district", "at", "large", "jackson",
               "priorities", "priority", "issues", "platform", "platforms", "policies", "positions", "answers",
               "sources", "questionnaire", "for", "if", "elected", "will", "you", "make", "your", "own"}
    if re.search(r"\b(property|assessment|assessments|appeals)\b", q):
        ignored |= {"property", "tax", "taxes", "assessments", "assessment", "appeals", "more", "fair", "fairness", "reform"}
        return "property" if set(q.split()) <= ignored else None
    return "issues" if set(q.split()) <= ignored else None


def add_to(corpus):
    entries = load()
    corpus.prepared_sources_ready = bool(entries)
    for entry in entries:
        ident = CONTEST + ":beacon:" + entry["topic"] + ":" + entry["candidate_name"].split()[-1].lower()
        corpus.evidence[ident] = {**entry, "id": ident, "contest_id": CONTEST, "source_id": "beacon-atlarge",
            "url": URL + "#" + entry["topic"], "title": "The Beacon · " + entry["question"],
            "issuer": "The Beacon / Josh Merchant", "source_category": "Published candidate questionnaire answer",
            "election_date": "2026-11-03", "snapshot_date": "2026-10-10", "publication_date": "2026-09-22",
            "version": "September 22 questionnaire; candidate statements as published, edited for length and clarity",
            "page": None, "column": None, "sha256": entry["archive_sha256"], "status": "current_snapshot",
            "extraction": "Full answer to this question; paragraph/list spacing normalized. Candidate claims are not independently verified",
            "original_route": "/api/prepared-source/beacon-atlarge", "original_label": "Retained questionnaire text ↗"}
    if entries:
        corpus.contests[CONTEST]["comparison_topics"] = QUESTIONS
        corpus.contests[CONTEST]["coverage"] = "Attributable questionnaire answers: priorities and property assessments. Other topics remain source gaps."


def original_text() -> bytes | None:
    entries = load()
    if not entries:
        return None
    header = f"The Beacon / Josh Merchant\nPublished 2026-09-22\n{URL}\nSelected complete answers; publisher edited responses for length and clarity.\n\n"
    return (header + "\n\n".join(f"{e['question']}\n{e['candidate_name']}\n{e['text']}" for e in entries)).encode()
