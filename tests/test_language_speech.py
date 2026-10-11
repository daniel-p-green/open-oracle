import unittest
from open_oracle.language_binding import LanguageBinding
from open_oracle.language_speech import language_speech_matches,canonical_transcript
from open_oracle.translation_validation import text_hash

class SpeechTests(unittest.TestCase):
    def test_all_six_exact_language_bound_transcripts_stale_audio_and_paraphrase(self):
        texts={'en':'The rate is 0.25 cent.','es':'La tasa es de 0.25 centavo.','vi':'Mức thuế là 0.25 xu.','ar':'المعدل هو 0.25 سنت.','zh-Hans':'税率为0.25美分。','fil':'Ang halaga ay 0.25 sentimo.'}
        for language,text in texts.items():
            core={'epoch':1,'generation':1,'request_id':'r','speech_id':'s'}
            binding=LanguageBinding(lambda _:core.update(generation=core['generation']+1),lambda t:t==core,language)
            contract={'ticket':binding.bind(core),'language':language,'text':text,'text_sha256':text_hash(text)}
            validate=lambda t:language_speech_matches(contract,t,binding,lambda _:True,lambda *_:True,b'not_real_audio')
            self.assertTrue(validate(text)) # authored transcript + audio-check stub only
            self.assertFalse(validate(text+' YES'))
            self.assertFalse(validate(text.replace('0.25','25')))
            binding.choose('es' if language!='es' else 'en');self.assertFalse(validate(text))

    def test_audio_guard_source_guard_and_output_language_remain_required(self):
        binding=LanguageBinding(lambda _:None,lambda _:True,'ar')
        c={'ticket':binding.bind({'epoch':1}),'language':'ar','text':'النص الأصلي','text_sha256':text_hash('النص الأصلي')}
        self.assertFalse(language_speech_matches(c,c['text'],binding,lambda _:True,lambda *_:False,None))
        self.assertFalse(language_speech_matches(c,c['text'],binding,lambda _:False,lambda *_:True,None))
        c['language']='en';self.assertFalse(language_speech_matches(c,c['text'],binding,lambda _:True,lambda *_:True,None))

    def test_unicode_normalization_is_conservative_and_control_characters_rejected(self):
        self.assertEqual(canonical_transcript('Españo\u006c'),canonical_transcript('Español'))
        self.assertNotEqual(canonical_transcript('si'),canonical_transcript('sí'))
        with self.assertRaises(ValueError):canonical_transcript('YES\u202eNO')

if __name__=='__main__':unittest.main()
