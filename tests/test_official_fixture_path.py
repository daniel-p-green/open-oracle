import unittest
from open_oracle.language_fixtures import official_fixtures,SCOPE,accepted_fixture_transport
from open_oracle.translation_validation import TranslationGate,TranslationDecisionsCheck

class OfficialFixtureTests(unittest.TestCase):
    def test_every_non_english_official_span_path_preserves_whole_original_and_offsets(self):
        sources,forms=official_fixtures()
        gate=TranslationGate(sources.get,forms,lambda _:None,TranslationDecisionsCheck(accepted_fixture_transport),lambda:None)
        original=next(iter(sources.values()))
        for language in ('es','vi','ar','zh-Hans','fil'):
            claims=[{'form_id':f.id,'text':f.target,'language':language} for f in forms if f.language==language]
            result=gate.release('official-fixture',language,claims,SCOPE,fixture_mode=True)
            self.assertEqual(result['status'],'fixture_validated',result)
            self.assertEqual(result['originals'][0]['text'],original.text)
            self.assertEqual(result['originals'][0]['original_sha256'],original.original_sha256)
            self.assertIsNone(result['speech'])
            for claim in result['translation']['claims']:
                self.assertEqual(original.text[claim['start']:claim['end']],claim['quote'])
        self.assertIn('Trust Fund',' '.join(original.text.split()))
        self.assertIn('YES',original.text);self.assertIn('NO',original.text)

if __name__=='__main__':unittest.main()
