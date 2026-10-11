import unittest
from open_oracle.language_binding import LanguageBinding
from open_oracle.language_session import LanguageSession
from open_oracle.language_capabilities import LanguageRegistry,direction,locale_tag
from open_oracle.localization import message,refusal

class StateTests(unittest.TestCase):
    def test_registry_independent_capabilities_and_six_native_labels(self):
        registry=LanguageRegistry().public()
        self.assertEqual([r['language'] for r in registry['languages']],['en','es','vi','ar','zh-Hans','fil'])
        self.assertFalse(any(r['spoken_ready'] for r in registry['languages']))
        self.assertEqual([r['voice'] for r in registry['languages']],['cedar',None,None,None,None,None])
        self.assertEqual(registry['provider_language_coverage'],'not_established')

    def test_rtl_script_and_supported_status_are_separate(self):
        self.assertEqual(direction('ar'),'rtl');self.assertEqual(direction('ar-Latn'),'ltr')
        self.assertEqual(direction('en-Arab'),'rtl');self.assertEqual(direction('ar','Official YES 10'),'ltr')
        self.assertEqual(message('control.stop','ar')['direction'],'rtl')
        self.assertEqual(refusal('service_failure','vi')['language'],'vi')
        m=message('control.stop','fr');self.assertEqual(m['language'],'en');self.assertEqual(m['fallback_reason'],'unsupported_language')
        registry=LanguageRegistry()
        self.assertIsNone(registry.resolve('ar-Latn'));self.assertIsNone(registry.resolve('zh-Hant'))
        self.assertEqual(registry.resolve('zh-Hans-CN').language,'zh-Hans')

    def test_invalid_tags_fail_and_region_preserved(self):
        self.assertEqual(locale_tag('es-mx'),'es-MX');self.assertEqual(locale_tag('ZH-hans'),'zh-Hans')
        for value in ('',None,'../es','en<script>','en_US','en-u-foo'):
            with self.assertRaises(ValueError):locale_tag(value)

    def test_binding_reuses_continuous_voice_identity_and_revision_fences_every_output(self):
        ticket={'epoch':1,'generation':1,'turn_id':'t','transcript_id':'x','request_id':'r'}
        stopped=[]
        def cancel(reason):stopped.append(reason);ticket['generation']+=1
        binding=LanguageBinding(cancel,lambda candidate:candidate==ticket)
        old=binding.bind(ticket);self.assertTrue(binding.accepts(old))
        binding.choose('ar');self.assertFalse(binding.accepts(old));self.assertEqual(stopped,['language_revision'])
        self.assertEqual(ticket['epoch'],1)
        current=binding.bind(ticket);self.assertTrue(binding.accepts(current))
        binding.correction('سؤال عن الضريبة','ar',current);self.assertFalse(binding.accepts(current))
        self.assertEqual(binding.corrected_transcript['language'],'ar');self.assertEqual(binding.language,'ar')
        binding.erase();self.assertIsNone(binding.corrected_transcript)

    def test_failed_cancellation_prevents_locale_mutation(self):
        def failure(_):raise RuntimeError('Cannot invalidate player')
        binding=LanguageBinding(failure,lambda _:True)
        with self.assertRaises(RuntimeError):binding.choose('es')
        self.assertEqual(binding.language,'en');self.assertEqual(binding.revision,0)
        binding=LanguageBinding(lambda _:False,lambda _:True)
        with self.assertRaisesRegex(ValueError,'cancellation_failed'):binding.choose('es')
        self.assertEqual(binding.language,'en');self.assertEqual(binding.revision,0)

    def test_isolated_fixture_session_stop_resume_erase_and_mixed_correction(self):
        calls=[];session=LanguageSession(lambda:calls.append(True))
        session.resume();old=session.token('r1');session.suggest(['en','es'],old)
        self.assertTrue(session.recognition['mixed']);self.assertEqual(session.language,'en')
        session.choose('es');self.assertFalse(session.accepts(old));self.assertTrue(session.stopped)
        session.resume();current=session.token('r2');session.correct_transcript('¿Qué cambia?','es',current)
        self.assertFalse(session.accepts(current));session.resume();current=session.token('r3')
        session.stop();self.assertFalse(session.accepts(current));self.assertIsNotNone(session.transcript)
        sid=session.session_id;session.erase();self.assertNotEqual(sid,session.session_id);self.assertIsNone(session.transcript)

if __name__=='__main__':unittest.main()
