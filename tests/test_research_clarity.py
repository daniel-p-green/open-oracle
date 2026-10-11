"""Public scripted offline clarity/source regression; not a Decisions pass claim."""
from copy import deepcopy
from unittest import TestCase
from open_oracle.corpus import Corpus
from open_oracle.research_release import FORMS,GAP,answer_from_checked_claims,research_reviewed,requested_parts
from open_oracle.research_display import project_display,validate_display
from test_research_release import BoundModel,Review

class ResearchClarityTests(TestCase):
    def response(self,question,authority='JCEB',review=None):
        return research_reviewed(question,authority=authority,model=BoundModel(),execution='synthetic_sdk',reviewer=review or Review(),display_adapter=project_display)
    def test_both_facts_define_combat_and_keep_conditional_original_units(self):
        r=self.response('What is the COMBAT rate and how long would it last?')
        self.assertEqual(r['answer'],"If voters approve the question, the county's anti-crime sales tax, called COMBAT, would continue for ten years. The proposed rate is one-quarter of one cent.")
        self.assertEqual(r['answer'].count('If voters approve'),1)
        self.assertEqual([c['text'] for c in r['claims']],list(FORMS.values()))
        self.assertIn('Trust Fund',' '.join(r['evidence'][0]['text'].split()))
        self.assertIn('YES',r['evidence'][0]['text'])
        self.assertEqual(validate_display(r,Corpus())['status'],'supported')
        self.assertNotRegex(r['answer'],r'%|\$|percent|each dollar')
    def test_single_facts_other_board_and_mixed_gap_have_exact_coverage(self):
        for question,parts in [('What is the COMBAT rate?',{'rate'}),('What is the COMBAT duration?',{'duration'}),('What is the COMBAT rate and will it reduce crime by 20%?',{'rate','prediction'})]:
            for board in ('JCEB','KCEB'):
                r=self.response(question,board)
                self.assertEqual(set(r['fact_validation']['covered_parts']),parts)
                self.assertEqual(r['evidence'][0]['authority'],board)
                self.assertIn('If voters approve the question',r['answer'])
                self.assertEqual('ten years' in r['answer'],'duration' in parts)
                self.assertEqual(GAP in r['answer'],'prediction' in parts)
                self.assertEqual(validate_display(r,Corpus())['status'],'supported')
    def test_prediction_only_remains_refusal_without_invented_facts(self):
        r=self.response('Will COMBAT reduce crime by 20 percent?')
        self.assertEqual(r['answer'],GAP);self.assertEqual(r['claims'],[])
        self.assertEqual(r['status'],'insufficient_evidence')
    def test_changed_conditions_amount_duration_and_added_percentage_still_held(self):
        r=self.response('What is the COMBAT rate and how long would it last?')
        variants=[r['answer'].replace('If voters approve the question, ',''),r['answer'].replace('one-quarter of one cent','one-quarter of one percent'),r['answer'].replace('ten years','twenty years'),r['answer']+' That is 0.25% or $0.25 on $100.',r['answer']+' It will reduce crime by 20%.']
        for text in variants:
            bad=deepcopy(r);bad['answer']=text
            self.assertEqual(validate_display(bad,Corpus())['status'],'unsupported')
        with self.assertRaises(ValueError):answer_from_checked_claims([{'text':'The tax is 0.25%.'}])
    def test_missing_part_unknown_topic_advice_and_review_rejection_do_not_turn_green(self):
        for q in ['How should I vote on COMBAT?','What is the COMBAT rate and current law?','What is the COMBAT rate and housing?','What is the COMBAT rate in percent?','What is the COMBAT rate and Question 2?']:
            with self.assertRaises(ValueError):requested_parts(q)
        class Rejected(Review):
            def review(self,e):return {'status':'rejected','execution':'offline_stub','threshold':0.95,'probabilities':{'clarity':0.94}}
        r=self.response('What is the COMBAT rate and how long would it last?',review=Rejected())
        self.assertFalse(r['public_display']);self.assertEqual(r['claims'],[]);self.assertEqual(r['evidence'],[])
        self.assertEqual(r['review']['threshold'],0.95)
