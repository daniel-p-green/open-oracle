"""Small question-to-evidence interface shared by HTTP, CLI, and evaluations."""
from __future__ import annotations

import re
import time
from uuid import uuid4

from .corpus import Corpus, ELECTION, SNAPSHOT, normalized
from .cards import measure_card, candidate_card
from .quality_policy import release_block
from .claim_bindings import validate_factual_display
from .source_fallback import make_fallback
from .view_plan import make_view_plan
from .session_control import check_cancel
from .readability import requested_span, build_readability_tool, diagnostic_answer
from .operational_receipts import new_receipt, current_receipt, record_release
from strands_quality.local_metrics import AggregateMetrics

OFFICIAL_LINKS = [
    {"title": "KCEB — Kansas City within Jackson County", "url": "https://www.kceb.org/"},
    {"title": "JCEB — Jackson County outside Kansas City", "url": "https://jcebmo.org/"},
    {"title": "Missouri Secretary of State — elections", "url": "https://www.sos.mo.gov/elections"},
]
RECOMMEND = re.compile(r"how should|who should|recommend|best candidate|better (?:candidate|on|for)|who is better|should i (?:vote|support)|tell me (?:who|how) to vote", re.I)
LOGISTICS = re.compile(r"polling|voter (?:id|identification)|register|registration|absentee|early vot|vote by mail|deadline|where (?:do|can|should) .*vote|voting hours", re.I)
POSITION = re.compile(r"position|policy|policies|compare|better|stance|approach|propert|assessment|differ|climate|accomplish|record|qualif|priority|priorities|support|rating|performance|transcript|said|platform|endors|experience|\b(?:views?|thinks?|believes?|opinions?|issues?|plans?|stands?)\b", re.I)


class EvidenceLoop:
    def __init__(self, corpus: Corpus, selector=None, reviewer=None):
        self.corpus = corpus
        self.selector = selector
        self.reviewer = reviewer
        self.operation_metrics = AggregateMetrics()

    def answer(self, question: str, scope: dict | None = None, request_id: str | None = None, contest_id: str | None = None) -> dict:
        receipt = new_receipt(self)
        token = current_receipt.set(receipt)
        response, error = None, None
        try:
            response = self._answer(question, scope, request_id, contest_id)
            record_release(receipt, response)
            if response.get("integration_error"):
                error = RuntimeError("Integration did not complete")
            return response
        except BaseException as exc:
            error = exc
            receipt.release(status="unavailable", binding="not_run", review="not_run", review_execution="not_run")
            raise
        finally:
            current_receipt.reset(token)
            snapshot = receipt.finish(error)
            self.operation_metrics.record(receipt)
            if response is not None:
                response["operational_receipt"] = snapshot

    def _answer(self, question: str, scope: dict | None = None, request_id: str | None = None, contest_id: str | None = None) -> dict:
        check_cancel()
        started = time.monotonic()
        scope = dict(scope or {})
        scope.pop("_comparison_topic", None)  # Only the application may choose this retrieval slice.
        scope.setdefault("election_date", ELECTION)
        question = question.strip()
        result = {
            "request_id": request_id or str(uuid4()), "status": "insufficient_evidence",
            "answer": "", "card": None, "evidence": [], "choices": [], "claims": [], "links": [], "candidate_sources": [],
            "scope": scope, "snapshot_date": SNAPSHOT, "election_date": ELECTION,
            "mode": "live_strands" if self.selector else "exact_source",
            "language": "en", "translation_status": "not_requested",
            "review": {"status": "not_run", "label": "Application checks only. Independent AI review has not run."},
            "limitations": ["Archived research snapshot. Samples are subject to change. This is not a personal ballot.",
                            "Exact source excerpts; a full legal-effect or candidate-position analysis is not available in this slice."],
            "trace": [],
        }

        def finish(status, answer):
            check_cancel()
            result["status"] = status
            result["answer"] = answer
            guard_started = time.monotonic()
            source_fallback = make_fallback(result, self.corpus)
            blocked = release_block(result, self.corpus)
            result['fact_validation'] = validate_factual_display(result, self.corpus) if not blocked else {'status': 'unsupported', 'reason': blocked, 'claims': []}
            if result['fact_validation']['status'] in ('unsupported', 'contradictory'):
                blocked = 'factual_binding_' + result['fact_validation']['status']

            guard_ms = round((time.monotonic() - guard_started) * 1000)
            review_started = time.monotonic()
            if blocked:
                result["review"] = {"status": "rejected", "execution": "deterministic_guard",
                                    "reason": blocked, "label": "Application release guard blocked this response."}
            elif self.reviewer and status == 'unavailable' and result.get('integration_error'):
                result['review'] = {'status': 'unavailable', 'execution': 'not_run',
                                    'label': 'Live retrieval could not complete. Only mechanically bound original wording is available.'}
            elif self.reviewer:
                check_cancel()
                envelope = {"question": question, "response": {k: v for k, v in result.items() if k not in ("trace", "elapsed_ms", "review", "request_id")}}
                result["review"] = self.reviewer.review(envelope)
                check_cancel()
            if blocked or (self.reviewer and result["review"]["status"] != "accepted"):
                result["status"] = "unavailable"
                result["answer"] = "Live retrieval could not complete. No checked explanation was released. Retained original wording may be available." if result["review"].get("execution") == "not_run" else "The quality checks did not accept this response. No checked answer was released. The contest inventory remains available."
                result["evidence"] = []
                result["claims"] = []
                result["candidate_sources"] = []
                result["card"] = None
                if source_fallback:
                    result['source_fallback'] = source_fallback
            result['stage_ms'] = {'resolve_retrieve_construct': round((guard_started - started) * 1000),
                                  'source_guards': guard_ms, 'decisions': round((time.monotonic() - review_started) * 1000)}
            # Reuse the exact accepted text: no extra rewrite model or weakened check.
            if (result['status'] == 'answered' and result['fact_validation']['status'] == 'supported'
                    and result['review'].get('execution') == 'real_api' and result['review']['status'] == 'accepted'
                    and result['language'] == 'en' and len(result['answer']) <= 1800 and 'readability' not in result):
                result['speech'] = {'request_id': result['request_id'], 'language': 'en', 'text': result['answer'],
                                    'evidence_bindings': [{'id': e['id'], 'sha256': e['sha256'], 'text': e['text']} for e in result['evidence']]}
            result['view_plan'] = make_view_plan(result, question)
            if result['status'] != 'answered':
                result.pop('readability', None)
            result["elapsed_ms"] = round((time.monotonic() - started) * 1000)
            return result

        if not question or len(question) > 2000:
            return finish("clarification", "Please enter a question of up to 2,000 characters.")
        if RECOMMEND.search(question):
            return finish("neutrality_boundary", "I can help explain the wording and show sources. I don't recommend candidates or how to vote. Ask about a contest or measure you want to understand.")
        if LOGISTICS.search(question):
            result["links"] = OFFICIAL_LINKS
            return finish("official_links", "For voting locations, ID rules, registration, and deadlines, use the official election authority. Choose KCEB for Kansas City within Jackson County or JCEB for the rest of Jackson County. Check the current instructions there.")
        if scope["election_date"] != ELECTION or re.search(r"\b(?:2024|2025)\b", question):
            return finish("insufficient_evidence", "This browser uses the November 3, 2026 research snapshot. Historical election evidence is kept separate and cannot answer this request.")
        if re.search(r"write.?in|declared candidate", question, re.I):
            result["links"] = OFFICIAL_LINKS
            return finish("insufficient_evidence", "The current November declared-write-in roster was not verified in this snapshot. Printed write-in lines do not identify declared candidates. Please check the election authority for current information.")
        if re.search(r"(?:my|your|our) ballot|eligible|eligibility|do i (?:get|vote on)|which (?:district|contests)", question, re.I):
            result["links"] = OFFICIAL_LINKS
            return finish("clarification", "I can explain a printed contest, but this inventory cannot assign your personal ballot. Use your election authority's official lookup to confirm applicable districts and contests.")
        if scope.get("authority") not in (None, "unknown", "KCEB", "JCEB"):
            return finish("clarification", "Choose KCEB, JCEB, or leave the election authority unknown.")
        if scope.get("authority") == "KCEB" and scope.get("municipality") not in (None, "", "Kansas City within Jackson County"):
            return finish("clarification", "That city selection conflicts with KCEB, which covers Kansas City within Jackson County. Please correct the scope.")
        contests = self.corpus.resolve(question, contest_id)
        if not contests:
            return finish("insufficient_evidence", "I couldn't identify a contest in this snapshot. Choose one from the inventory, or enter its name or measure number.")
        if len(contests) > 1:
            result["choices"] = [{"id": c["id"], "title": c["title"]} for c in contests]
            return finish("clarification", "More than one contest matches. Please choose the contest you mean.")
        contest = contests[0]
        result["contest"] = {k: v for k, v in contest.items() if k != "aliases"}
        if not self.corpus.allowed(contest, scope):
            location = contest["required_location"]
            result["required_scope"] = {"field": "district" if contest["scope"] == "district" else "municipality", "value": location}
            return finish("clarification", f"This question is specific to {location}. Confirm the relevant city or district before retrieving its wording. That confirmation still does not establish personal eligibility.")
        comparison_topic = None
        comparison_request = None
        combat_parts = None
        if contest["kind"] in ("candidate", "retention") and (POSITION.search(question) or re.search(r"\b(?:sources?|questionnaires?|surveys?|background|evidence|answers?)\b", question, re.I)):
            # Validate all named identities even when an explicit contest overrides
            # the resolver. A surname from another race is never an unknown topic.
            query = ' ' + normalized(question) + ' '
            local_surnames = {normalized(p['name']).split()[-1] for p in contest.get('candidates', [])}
            foreign = [c['id'] for c in self.corpus.contests.values() if c['id'] != contest['id']
                       and any(' ' + normalized(p['name']) + ' ' in query or
                               (normalized(p['name']).split()[-1] not in local_surnames and
                                ' ' + normalized(p['name']).split()[-1] + ' ' in query)
                               for p in c.get('candidates', []))]
            if contest['id'] == 'county-legislator-1st-district-at-large' and foreign:
                result['choices'] = [{'id': ident, 'title': self.corpus.contests[ident]['title']}
                                     for ident in sorted(set(foreign + [contest['id']]))]
                return finish('clarification', 'The named people do not all match this contest. Please choose the contest and candidate identity you mean; I will not attach another person’s answers.')
            catalog = self.corpus.candidate_sources.lookup(contest, question, scope)
            if catalog["conflicts"]:
                result["choices"] = [{"id": ident, "title": self.corpus.contests[ident]["title"]} for ident in catalog["conflicts"]]
                return finish("clarification", "The named people do not all match this contest. Please choose the contest and candidate identity you mean; I won't attach one person's sources to another.")
            from .demo_sources import CONTEST, comparison_parts
            if contest["id"] == CONTEST and self.corpus.prepared_sources_ready:
                comparison_request = comparison_parts(question)
                if comparison_request['topics']:
                    comparison_topic = comparison_request['topics'][0]
                    known = {'climate','crime','abortion','immigration','records and experience','stadiums and sports','sales taxes','endorsements'}
                    comparison_request['gaps'] = [g for g in comparison_request['gaps'] if g in known] + (['other_requested_topic'] if comparison_request['unclassified'] else [])
                    result['comparison_request'] = comparison_request
            if comparison_topic is None:
                return self._candidate_gap(result, catalog, finish)
        if contest['id'] == 'combat' and re.search(r'\brate\b|how long|\bduration\b', question, re.I):
            from .research_release import requested_parts
            try: combat_parts = sorted(requested_parts(question))
            except ValueError:
                return finish('insufficient_evidence', 'Your full request is outside the checked COMBAT rate/duration explanation. No subquestion was silently answered; inspect the retained wording or ask one supported part.')
        retrieval_scope = {**scope, "_comparison_topic": comparison_topic} if comparison_topic else scope
        related = [e for e in self.corpus.evidence.values() if e["contest_id"] == contest["id"]
                   and (e.get("topic") == comparison_topic if comparison_topic else "topic" not in e)]
        if any(e["status"] == "conflict" for e in related):
            return finish("conflict", "The retained source checksum no longer matches the inspected snapshot. I cannot release its wording until the source version is reconciled.")
        if self.selector:
            try:
                selected, trace = self.selector(question, retrieval_scope, contest["id"], self.corpus)
                result["trace"] = trace
                analyses = [step.pop("readability_analysis") for step in trace if "readability_analysis" in step]
                if analyses:
                    result["readability"] = {"execution": "strands_tool_agent", "reports": analyses}
            except Exception as exc:
                result["integration_error"] = type(exc).__name__
                result["evidence"] = self.corpus.search(contest["id"], retrieval_scope)
                return finish("unavailable", "The live evidence workflow could not finish. Switch to exact-source mode to inspect retained wording. No generated answer has been released.")
        else:
            evidence = self.corpus.search(contest["id"], retrieval_scope)
            selected = [e["id"] for e in evidence]
            result["trace"] = [{"tool": "local_lookup", "evidence_ids": selected, "live": False}]
            span = requested_span(question)
            if span and contest["kind"] == "measure" and selected:
                try:
                    report = build_readability_tool(self.corpus, retrieval_scope)(evidence_id=selected[0], span=span)
                    result["readability"] = {"execution": "strands_tool_direct", "reports": [report]}
                    result["trace"].append({"tool": "test_ballot_readability", "evidence_ids": [selected[0]], "live": False})
                except ValueError:
                    result["readability"] = {"execution": "strands_tool_direct", "status": "unavailable", "reason": "The requested policy span is not available in the retained evidence."}
        if comparison_request and len(comparison_request['topics']) == 2:
            # Existing optional live selector only covers one topic. Never add
            # unread second-topic evidence after a live request or paid review.
            if self.selector:
                return finish('insufficient_evidence', 'This live selector can read one questionnaire topic per request. Please ask priorities or property taxes separately; both sources are retained.')
            evidence = [e for topic in comparison_request['topics'] for e in self.corpus.search(contest['id'], {**scope, '_comparison_topic': topic})]
            selected = [e['id'] for e in evidence]
            result['trace'] = [{'tool': 'local_lookup', 'evidence_ids': selected, 'live': False}]
            # Each topic is read through its own existing scoped read guard.
            evidence = [self.corpus.read(e['id'], {**scope, '_comparison_topic': e['topic']}) for e in evidence]
        if not (comparison_request and len(comparison_request['topics']) == 2):
            evidence = [self.corpus.read(ident, retrieval_scope) for ident in selected]
        if not evidence or any(e is None or e["contest_id"] != contest["id"] for e in evidence):
            return finish("insufficient_evidence", "No applicable current-snapshot passage was returned. I won't fill the gap with an unsourced answer.")
        # Ballot wording lists purposes; it does not establish measured results or predictions.
        if contest["id"] == "combat" and not (combat_parts and set(combat_parts)-{'prediction'}) and re.search(r"reduce.{0,35}(?:crime|percent|%)|(?:crime|effectiv|results?|success).{0,35}(?:rate|percent|%|reduc|prove)|how much.{0,35}(?:crime|save|cost)|guarantee", question, re.I):
            result["links"] = [{"title": "Retained official wording", "url": evidence[0]["original_route"]}]
            return finish("insufficient_evidence", "The retained ballot question states COMBAT's purposes. It does not establish how much crime it would reduce or prove its effectiveness. I cannot support that prediction from this wording.")
        if comparison_topic:
            card = candidate_card(contest, evidence, comparison_topic)
            if not card:
                return finish("insufficient_evidence", "The comparison requires both candidates' complete answers to the same question. The returned evidence was incomplete; no comparison was released.")
            result["card"] = card
            from .claim_bindings import comparison_answer
            answer = comparison_answer(comparison_request)
            result["limitations"][1] = "Prepared comparison covers priorities and property assessments for District 1 At-Large. Other races and topics remain source gaps."
        elif contest["kind"] == "candidate":
            answer = "The retained official sample shows the printed roster below. The names also appear in the inventory. Position comparisons need additional original, attributed sources."
        elif contest["kind"] == "retention":
            answer = "This is a judicial retention question: whether the named judge stays in office. The official question is below. This slice does not assess the judge or recommend a response."
        else:
            answer = "The official sample asks the question below. Its wording is evidence of the printed question; it is not an endorsement or a prediction of every legal effect. Read the original document alongside it."
        result["evidence"] = evidence
        result["claims"] = [{"quote": e["text"], "evidence_id": e["id"]} for e in evidence]
        if not comparison_topic:
            result["card"] = measure_card(question, contest, evidence)
            if result["card"]:
                answer = ("A NO vote rejects the proposal to continue the COMBAT sales tax. The sample does not explain what happens if the proposal fails."
                          if re.search(r"what does no mean", question, re.I) else
                          "This question asks whether Jackson County should continue the COMBAT sales tax for ten years. You can read one part at a time below.")
        if (result.get('card') or {}).get('type') == 'measure_explanation':
            focus = make_view_plan({**result, 'status': 'answered'}, question)
            if focus and focus['component'] == 'measure_focus' and focus['initial_part'] > 0:
                from .cards import FACETS
                answer = FACETS[focus['initial_part']][1]
        if combat_parts and set(combat_parts)-{'prediction'}:
            from .claim_bindings import combat_parts_answer
            result['requested_parts'] = combat_parts
            answer = combat_parts_answer(combat_parts)
        if result.get('readability', {}).get('reports'):
            diagnostic = diagnostic_answer(result['readability'])
            if diagnostic:
                answer = diagnostic
                result['card'] = None  # Only the requested diagnostic plus its complete bound original.
                result['limitations'] = [
                    'Saved sample ballot; it may change. This is not your personal ballot.',
                    'The counts cover only the selected English wording. Numbers and names can change these estimates.',
                    'This is a wording check, not a full legal explanation.']
        return finish("answered", answer)

    def _candidate_gap(self, result, catalog, finish):
        result["candidate_sources"] = catalog["people"]
        result["links"] = [{"title": "Official KCEB sample", "url": "https://kceb.org/elections/ballot/"},
                           {"title": "Official JCEB sample", "url": "https://jcebmo.org/election-information/on-the-ballot/"}]
        result["trace"] = [{"tool": "candidate_source_catalog", "live": False,
                            "candidate_ids": [p["candidate_id"] for p in catalog["people"]], "position_text_retrieved": False}]
        result["limitations"].append("Candidate-statement links and research coverage metadata are not quoted position evidence. Retained judicial surveys are third-party evaluations, not this app's ratings or voting advice.")
        catalog_note = ("The candidate-specific source pointers and any retained survey originals are shown below; opening a publisher link may provide information not retained here."
                        if catalog.get("available") and catalog["people"] else
                        "The pinned source catalog has no verified pointers to show for this request. The official samples are linked below.")
        if result["contest"]["id"] == "county-legislator-1st-district-at-large" and self.corpus.prepared_sources_ready:
            return finish("insufficient_evidence", "The prepared Pollard–Fields comparison covers their stated priorities and property-assessment proposals. It does not establish their views on the topic requested. Ask to compare priorities or property taxes; other source pointers appear below.")
        return finish("insufficient_evidence", "I don't have original attributable candidate-position answers or an independent performance assessment indexed for this request. That is a source gap, not a judgment about any candidate or judge. " + catalog_note)
