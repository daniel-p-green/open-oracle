from copy import deepcopy
import unittest
from open_oracle.corpus import Corpus
from open_oracle.engine import EvidenceLoop
from open_oracle.quality_policy import release_block,review_projection
from open_oracle.claim_bindings import validate_factual_display
from open_oracle.readability import verify_diagnostic

class DiagnosticReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.c=Corpus()
    def response(self):return EvidenceLoop(self.c).answer('What is the COMBAT reading level?',{'authority':'JCEB'})
    def test_answer_is_responsive_verified_estimate_not_comprehension(self):
        r=self.response();self.assertEqual(r['status'],'answered');self.assertIn('scores 21.85 on a scale based on school reading grades',r['answer'])
        self.assertIn('do not tell us whether someone understands',r['answer']);self.assertTrue(verify_diagnostic(r,self.c));self.assertTrue(verify_diagnostic(r))
        self.assertEqual(validate_factual_display(r,self.c)['computed_diagnostic'],'recomputed_exact_match');self.assertNotIn('speech',r)
        projected=review_projection({'response':r});self.assertEqual(projected['computed_diagnostics'][0]['scores'],r['readability']['reports'][0]['scores'])
    def test_forged_score_counts_source_hash_span_method_and_prose_fail_closed(self):
        mutations=[lambda r:r['readability']['reports'][0]['scores'].update(flesch_kincaid_grade_level=1),
            lambda r:r['readability']['reports'][0]['counts'].update(words=1),
            lambda r:r['readability']['reports'][0].update(raw_text_sha256='0'*64),
            lambda r:r['readability']['reports'][0].update(method_version='forged'),
            lambda r:r['readability']['reports'][0]['provenance'].update(span='fiscal_summary'),
            lambda r:r.update(answer='This proves the wording is easy to understand.')]
        for change in mutations:
            r=self.response();change(r)
            self.assertFalse(verify_diagnostic(r,self.c));self.assertEqual(release_block(r,self.c),'computed_diagnostic_unbound')
            self.assertEqual(validate_factual_display(r,self.c)['status'],'unsupported')
    def test_malformed_score_rejected_without_crash(self):
        r=self.response();r['readability']['reports'][0]['scores']=None
        self.assertEqual(release_block(r,self.c),'computed_diagnostic_unbound')
        self.assertEqual(validate_factual_display(r,self.c)['status'],'unsupported')
    def test_regular_combat_answer_and_original_preserved(self):
        r=EvidenceLoop(self.c).answer('What is the COMBAT tax rate?')
        self.assertEqual(r['status'],'answered');self.assertNotIn('readability',r)
        self.assertIn('separate from the general fund',r['evidence'][0]['text'])
        for invalid in (None,'',[],1):
            changed=deepcopy(r);changed['answer']=invalid
            self.assertEqual(validate_factual_display(changed,self.c)['status'],'unsupported')
if __name__=='__main__':unittest.main()
