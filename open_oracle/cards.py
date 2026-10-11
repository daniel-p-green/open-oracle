"""Predefined explanation facets; never arbitrary model-generated UI or prose."""
import re
from typing import Literal
from pydantic import BaseModel, Field
from .corpus import ELECTION, JCEB_HASH

class Facet(BaseModel):
    title: str
    statement: str
    quote: str
    evidence_id: str
    start: int = Field(ge=0)
    end: int = Field(gt=0)

class MeasureCard(BaseModel):
    type: Literal["measure_explanation"]
    id: str
    contest_id: Literal["combat"]
    election_date: Literal["2026-11-03"]
    jurisdiction: Literal["Jackson County, Missouri"]
    evidence_id: Literal["combat:jceb-sample"]
    source_sha256: str
    source_url: str
    presentation: Literal["overview", "step_by_step", "choice_focus"]
    title: str
    facets: list[Facet] = Field(min_length=5, max_length=5)
    limit: str
    method: str

CHOICE = re.compile(r"what does (?:yes|no) mean", re.I)
CONFUSION = re.compile(r"still.{0,12}(?:don['’]?t understand|confused)|simpler|one (?:thing|step) at a time|break.{0,8}down", re.I)
EXPECTED = "QUESTION # 1 Shall Jackson County continue its anti-crime sales tax, commonly known as COMBAT, at the rate of one-quarter of one cent for a period of ten years for the purpose of promoting and providing public safety within Jackson County, including the prevention and treatment of drug abuse and addiction and the prevention, investigation, prosecution, and detention of violent criminals and drug dealers? The proceeds of this tax shall be deposited in a special Jackson County Anti-Crime Sales Tax Trust Fund, separate from the general fund or any other county funds. YES NO"
FACETS = (
    ("The decision", "YES approves the proposal to continue the COMBAT sales tax. NO rejects that proposal.", "Shall Jackson County continue its anti-crime sales tax"),
    ("The rate", "The printed tax rate is one-quarter of one cent.", "at the rate of one-quarter of one cent"),
    ("The time", "The proposed continuation lasts ten years.", "for a period of ten years"),
    ("The stated purpose", "The wording lists public safety, drug abuse prevention and treatment, and actions involving violent criminals and drug dealers.", "for the purpose of promoting and providing public safety within Jackson County, including the prevention and treatment of drug abuse and addiction and the prevention, investigation, prosecution, and detention of violent criminals and drug dealers"),
    ("Where the money goes", "The wording puts the money in a separate county anti-crime trust fund.", "The proceeds of this tax shall be deposited in a special Jackson County Anti-Crime Sales Tax Trust Fund, separate from the general fund or any other county funds."),
)

def measure_card(question, contest, evidence):
    if contest['id'] == 'amendment-7':
        from .amendment7 import card
        return card(question, contest, evidence)
    if contest["id"] != "combat":
        return None
    source = next((e for e in evidence if e["id"] == "combat:jceb-sample"), None)
    if not source or source["status"] != "current_snapshot" or source["sha256"] != JCEB_HASH or source["election_date"] != ELECTION:
        return None
    # Rephrases are approved only for this entire pinned passage, not matching keywords.
    if " ".join(source["text"].split()) != EXPECTED:
        return None
    facets = []
    for title, statement, quote in FACETS:
        pattern = r"\s+".join(re.escape(word) for word in quote.split())
        match = re.search(pattern, source["text"])
        if not match:
            return None
        facets.append({"title": title, "statement": statement, "quote": match.group(),
                       "evidence_id": source["id"], "start": match.start(), "end": match.end()})
    return MeasureCard.model_validate({"type": "measure_explanation", "id": "combat-explanation-v1", "contest_id": "combat",
            "election_date": ELECTION, "evidence_id": source["id"], "source_sha256": source["sha256"], "source_url": source["url"], "jurisdiction": "Jackson County, Missouri",
            "presentation": "choice_focus" if CHOICE.search(question) else "step_by_step" if CONFUSION.search(question) else "overview",
            "title": "What the COMBAT question asks", "facets": facets,
            "limit": "This is a retained sample, not a confirmed personal ballot. It explains the printed question, not every consequence of passage or rejection. It does not recommend a response.",
            "method": "Predefined explanation checked against retained wording; independent AI review follows the response label."}).model_dump()


def candidate_card(contest, evidence, topic):
    from .demo_sources import CONTEST, PASSAGE_HASHES, QUESTIONS, digest
    if contest["id"] != CONTEST or topic not in QUESTIONS:
        return None
    responses = []
    for candidate in contest["candidates"]:
        matches = [e for e in evidence if e.get("candidate_name") == candidate["name"] and e.get("topic") == topic
                   and e["contest_id"] == CONTEST and e["election_date"] == ELECTION and e["status"] == "current_snapshot"
                   and digest(e["text"].encode()) == PASSAGE_HASHES.get(topic + ":" + candidate["name"])]
        if len(matches) != 1:
            return None
        e = matches[0]
        responses.append({"candidate_name": candidate["name"], "party": candidate["party"], "quote": e["text"],
                          "evidence_id": e["id"], "passage_sha256": e["passage_sha256"]})
    card = {"type": "candidate_comparison", "id": "atlarge-1-" + topic + "-v1", "contest_id": CONTEST,
            "title": QUESTIONS[topic], "topic": topic, "responses": responses,
            "method": "Both candidates answering the same Beacon questionnaire, published September 22, 2026. Full answers as published; paragraph and list spacing normalized.",
            "limit": "These are candidate statements, not verified outcomes or an endorsement. The publisher edited responses for length and clarity. Other topics are not inferred from these answers."}

    if {e.get('topic') for e in evidence} == {'issues', 'property'}:
        sections = []
        for key in QUESTIONS:
            section = candidate_card(contest, [e for e in evidence if e.get('topic') == key], key)
            if section is None:
                return None
            sections.append({field: section[field] for field in ('topic', 'title', 'responses')})
        card['sections'] = sections
    return card
