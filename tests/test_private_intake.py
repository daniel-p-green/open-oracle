"""Actual private API/session races; offline arithmetic, no provider/media calls."""
import json
import threading
import unittest
from dataclasses import replace
from uuid import uuid4
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from unittest.mock import patch

from open_oracle.ballot_intake import IntakeContext, parse_paste
from open_oracle.private_intake import PrivateIntake, IntakeFailure
from open_oracle.session_control import VisitorSessions, SessionCancelled
from open_oracle.server import make_server
from open_oracle.engine import EvidenceLoop

TEXT = 'Question 1\nShall the county continue a tax of 0.25 cent for ten years? The money must remain in a separate trust fund.\nQuestion 2\nShall a second program continue?'


def ticket(n=0, **extra):
    return {'request_id': 'private-' + str(n), 'epoch': 0, 'sequence': n, **extra}


class PrivateStoreTests(unittest.TestCase):
    def setUp(self):
        self.sessions = VisitorSessions()
        self.store = PrivateIntake(self.sessions)
        self.session = str(uuid4())
        self.signal = self.sessions.begin(self.session)

    def prepare(self, text=TEXT, n=0, revision=0):
        return self.store.prepare(self.session, self.signal, ticket(n), revision, text=text)

    def commit(self, text=TEXT):
        prepared = self.prepare(text)
        result, self.signal = self.store.commit(self.session, self.signal, prepared['prepared_id'], ticket(1), 0)
        return result

    def test_preview_exact_unicode_private_and_no_acceptance(self):
        preview = self.prepare('Question 1\nA 🗳 ballot café?')
        doc = preview['document']
        self.assertEqual(doc['text'], 'Question 1\nA 🗳 ballot café?')
        self.assertEqual(doc['questions'][0]['end'], len(doc['text']))
        self.assertEqual(doc['source_locale'], 'unknown')
        self.assertFalse(doc['original_verified']); self.assertIsNone(doc['official_source_receipt'])
        self.assertEqual(self.sessions.entries[self.session]['receipt'], None)

    def test_two_phase_commit_requires_fresh_complete_same_owner_ticket(self):
        preview = self.prepare()
        for invalid in [ticket(0), ticket(1, language_revision=1), {**ticket(1), 'epoch': 1}]:
            with self.assertRaises(IntakeFailure):
                self.store.commit(self.session, self.signal, preview['prepared_id'], invalid, 0)
        old = self.signal
        result, self.signal = self.store.commit(self.session, self.signal, preview['prepared_id'], ticket(1), 0)
        self.assertTrue(old.is_set()); self.assertFalse(self.signal.is_set())
        self.assertEqual(result['document_revision'], 1)
        self.assertEqual(result['document']['owner_ticket'], ticket(1))
        with self.assertRaises(IntakeFailure):
            self.store.commit(self.session, self.signal, preview['prepared_id'], ticket(2), 0)

    def test_unknown_no_method_is_not_silently_scored(self):
        doc = self.commit()
        result, self.signal = self.store.select(self.session, self.signal, doc['document_id'], 'q1', ticket(2), 1, True, None)
        self.assertEqual(result['readability']['status'], 'unsupported')
        self.assertIsNone(result['readability']['report'])
        self.assertEqual(result['quote'], TEXT[:TEXT.index('Question 2')])
        self.assertIn('separate trust fund', result['quote'])
        self.assertEqual(result['source_locale'], 'unknown')

    def test_explicit_formula_is_conditional_and_bound_to_complete_quote(self):
        doc = self.commit()
        result, self.signal = self.store.select(self.session, self.signal, doc['document_id'], 'q1', ticket(2), 1, True, 'en')
        diagnostic = result['readability']
        self.assertEqual(diagnostic['status'], 'calculated_under_assumption')
        self.assertEqual(diagnostic['report']['raw_text_sha256'], result['binding']['quote_sha256'])
        self.assertEqual(diagnostic['source_locale'], 'unknown')
        self.assertIn('source language not verified', diagnostic['qualifier'])
        self.assertEqual(diagnostic['report']['factual_fidelity_status'], 'not_evaluated')
        self.assertEqual(diagnostic['clarity']['status'], 'not_run')
        self.assertFalse(result['speech']); self.assertEqual(result['translation'], 'blocked')
        self.assertNotIn('execution', diagnostic)
        self.assertNotIn('raw_text', diagnostic['report'])

    def test_whole_multi_question_is_labelled_document_not_question(self):
        doc = self.commit()
        result, self.signal = self.store.select(self.session, self.signal, doc['document_id'], 'whole', ticket(2), 1, True, 'en')
        self.assertEqual(result['readability']['scope'], 'whole_document')
        self.assertEqual(result['quote'], TEXT)

    def test_accented_text_remains_exact_and_unsupported(self):
        doc = self.commit('Question 1\nShall the café stay open?')
        result, self.signal = self.store.select(self.session, self.signal, doc['document_id'], 'q1', ticket(2), 1, True, 'en')
        self.assertIn('café', result['quote'])
        self.assertEqual(result['readability']['status'], 'unsupported')
        self.assertIsNone(result['readability']['report']['scores'])

    def test_ascii_spanish_does_not_become_verified_english(self):
        doc = self.commit('Question 1\nDebe el condado mantener el impuesto por diez anos?')
        result, self.signal = self.store.select(self.session, self.signal, doc['document_id'], 'q1', ticket(2), 1, True, 'en')
        self.assertEqual(result['readability']['status'], 'calculated_under_assumption')
        self.assertEqual(result['source_locale'], 'unknown')
        self.assertEqual(result['readability']['diagnostic_basis'], 'explicit_english_formula_assumption')

    def test_known_non_english_cannot_be_overridden(self):
        doc = self.commit()
        state = self.sessions.entries[self.session]['intake']; original = state['documents'][doc['document_id']]
        selected = __import__('open_oracle.ballot_intake', fromlist=['select_question']).select_question(original, 'q1', original.context, confirmed_complete=True)
        result = self.store._readability(replace(original, source_locale='es'), selected, 'en')
        self.assertEqual(result['status'], 'unsupported'); self.assertIsNone(result['report'])
        self.assertEqual(result['reason'], 'known_non_english_source')

    def test_dependency_missing_is_unavailable_not_zero(self):
        doc = self.commit()
        with patch('open_oracle.private_intake.version', side_effect=RuntimeError('PRIVATE_DIAGNOSTIC')):
            result, self.signal = self.store.select(self.session, self.signal, doc['document_id'], 'q1', ticket(2), 1, True, 'en')
        self.assertEqual(result['readability']['status'], 'unavailable')
        self.assertIsNone(result['readability']['report'])
        self.assertNotIn('PRIVATE_DIAGNOSTIC', json.dumps(result))

    def test_empty_formula_has_null_scores_never_zero(self):
        doc = self.commit('.')
        result, self.signal = self.store.select(self.session, self.signal, doc['document_id'], 'whole', ticket(2), 1, True, 'en')
        self.assertEqual(result['readability']['status'], 'empty')
        self.assertIsNone(result['readability']['report']['scores'])
        self.assertEqual(result['readability']['scope'], 'whole_document')

    def test_source_change_cancels_previous_work_and_clears_receipt_context(self):
        entry = self.sessions.entries[self.session]; entry['receipt']={'private':True}; entry['context']={'contest_id':'combat'}
        old = self.signal
        self.commit()
        self.assertTrue(old.is_set()); self.assertIsNone(entry['receipt']); self.assertNotIn('context',entry)
        with self.assertRaises(SessionCancelled): self.sessions.deliver(self.session, old, lambda: self.fail('late delivery'))
        with patch('open_oracle.session_control.accepted_speech', return_value={'fake':True}):
            self.sessions.retain(self.session, {'fake':'old'}, None, signal=old)
        self.assertIsNone(entry['receipt'])

    def test_erase_removes_all_documents_pending_scores_and_tombstones_session(self):
        self.commit()
        entry = self.sessions.entries[self.session]
        self.sessions.erase(self.session)
        self.assertNotIn('intake', entry)
        self.assertTrue(self.signal.is_set())
        with self.assertRaises(SessionCancelled): self.store.state(self.session, self.signal)
        with self.assertRaises(SessionCancelled): self.sessions.begin(self.session)

    def test_ttl_prunes_document_bytes_and_invalidates_old_signal(self):
        clock=[0]; self.sessions=VisitorSessions(now=lambda:clock[0], ttl=10)
        self.store=PrivateIntake(self.sessions); self.signal=self.sessions.begin(self.session)
        self.commit(); old=self.signal; self.sessions.end(self.session); clock[0]=11
        other=str(uuid4()); self.sessions.begin(other)
        self.assertNotIn(self.session, self.sessions.entries); self.assertTrue(old.is_set())

    def test_four_document_and_bytes_caps_are_enforced(self):
        for revision in range(4):
            prepared = self.prepare(n=revision*2, revision=revision)
            _, self.signal = self.store.commit(self.session, self.signal, prepared['prepared_id'], ticket(revision*2+1), revision)
        with self.assertRaises(IntakeFailure) as error: self.prepare(n=8,revision=4)
        self.assertEqual(error.exception.status, 413)
        self.sessions.erase(self.session)
        self.session=str(uuid4()); self.signal=self.sessions.begin(self.session)
        self.store.MAX_RAW_BYTES=2
        with self.assertRaises(IntakeFailure): self.prepare()
        self.assertIsNone(self.sessions.entries[self.session]['intake']['pending'])

    def test_pending_preview_invalidated_by_selection(self):
        doc=self.commit(); preview=self.prepare(n=2,revision=1)
        _,self.signal=self.store.select(self.session,self.signal,doc['document_id'],'q1',ticket(3),1,True,None)
        with self.assertRaises(IntakeFailure): self.store.commit(self.session,self.signal,preview['prepared_id'],ticket(4),1)

    def test_no_partial_confirmation_or_client_ranges(self):
        doc=self.commit()
        for block, confirmed in [('forged',True),('q1',False),('q1',1)]:
            with self.assertRaises(ValueError): self.store.select(self.session,self.signal,doc['document_id'],block,ticket(2),1,confirmed,None)
        self.assertEqual(self.store.state(self.session,self.signal)['selection_id'],None)

    def test_cancel_during_formula_preparation_does_not_install(self):
        doc=self.commit()
        def erased(*args): self.sessions.erase(self.session); return {'status':'unavailable'}
        with patch.object(self.store,'_readability',side_effect=erased):
            with self.assertRaises(SessionCancelled): self.store.select(self.session,self.signal,doc['document_id'],'q1',ticket(2),1,True,'en')
        self.assertNotIn('intake',self.sessions.entries[self.session])


class PrivateHttpTests(unittest.TestCase):
    def setUp(self):
        self.server=make_server(port=0,intake=True,operations=True)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.origin='http://127.0.0.1:'+str(self.server.server_port);self.session=str(uuid4())

    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join(2)

    def post(self,path,body=None,*,raw=None,headers=None,session=None):
        h={'Origin':self.origin,'Content-Type':'application/json','X-Oracle-Session':session or self.session}
        h.update(headers or {})
        request=Request(self.origin+path,data=raw if raw is not None else json.dumps(body).encode(),headers=h)
        try:
            with urlopen(request,timeout=10) as response: return response.status,json.load(response),dict(response.headers)
        except HTTPError as error: return error.code,json.load(error),dict(error.headers)

    def prepare(self,text=TEXT,n=0,revision=0):
        return self.post('/api/intake/prepare',{'owner_ticket':ticket(n),'expected_revision':revision,'text':text})

    def commit(self,text=TEXT):
        code,prepared,_=self.prepare(text);self.assertEqual(code,200)
        code,result,_=self.post('/api/intake/commit',{'prepared_id':prepared['prepared_id'],'owner_ticket':ticket(1),'expected_revision':0})
        self.assertEqual(code,200);return result

    def select(self,doc,method=None,**changes):
        data={'document_id':doc['document_id'],'block_id':'q1','owner_ticket':ticket(2),'expected_revision':1,'confirmed_complete':True,'method_language_assumption':method}
        data.update(changes);return self.post('/api/intake/select',data)

    def test_enabled_health_and_loopback_guards(self):
        with urlopen(self.origin+'/api/health') as response: health=json.load(response)
        self.assertTrue(health['intake']['enabled']);self.assertEqual(health['provider'],None)
        for kwargs in [{'host':'0.0.0.0'}, {'allowed_hosts':['venue.example']}]:
            with self.assertRaises(ValueError):make_server(port=0,intake=True,**kwargs)
        plain=make_server(port=0)
        try:
            thread=threading.Thread(target=plain.serve_forever,daemon=True);thread.start()
            request=Request('http://127.0.0.1:'+str(plain.server_port)+'/api/intake/state',data=b'{}',headers={'Content-Type':'application/json'})
            with self.assertRaises(HTTPError) as error:urlopen(request)
            self.assertEqual(error.exception.code,503)
        finally:plain.shutdown();plain.server_close();thread.join()

    def test_origin_host_session_are_mandatory(self):
        for headers,expected in [({'Origin':'http://evil.example'},403),({'X-Oracle-Session':'wrong'},400),({'Host':'evil.example'},403),({'Origin':''},403)]:
            self.assertEqual(self.post('/api/intake/state',{},headers=headers)[0],expected)

    def test_strict_json_unknown_keys_nonfinite_duplicate_and_utf16(self):
        for body in [b'[]',b'{"x":1}',b'{"x":1,"x":2}',b'{"x":NaN}', '{}'.encode('utf-16'),b'{"owner_ticket":"SECRET_PROVIDER_DIAGNOSTIC"}']:
            status,result,_=self.post('/api/intake/state',raw=body)
            self.assertEqual(status,400);self.assertNotIn('SECRET_PROVIDER_DIAGNOSTIC',json.dumps(result))
        self.assertEqual(self.post('/api/intake/prepare',{'owner_ticket':ticket(),'expected_revision':0,'text':'hi','original_verified':True})[0],400)

    def test_preview_commit_selection_formula_erase_actual_http(self):
        doc=self.commit();status,result,headers=self.select(doc,'en')
        self.assertEqual(status,200);self.assertEqual(headers['Cache-Control'],'no-store')
        self.assertEqual(result['readability']['status'],'calculated_under_assumption')
        self.assertIn('separate trust fund',result['quote']);self.assertFalse(result['speech'])
        self.assertEqual(self.post('/api/erase',{})[0],200)
        self.assertEqual(self.post('/api/intake/state',{})[0],410)
        self.assertEqual(self.post('/api/intake/state',{},session=str(uuid4()))[1]['documents'],[])

    def test_session_cross_binding_client_ranges_revision_and_ticket_replay(self):
        doc=self.commit()
        self.assertEqual(self.post('/api/intake/select',{'document_id':doc['document_id'],'block_id':'q1','owner_ticket':ticket(2),'expected_revision':0,'confirmed_complete':True,'method_language_assumption':'en'},session=str(uuid4()))[0],409)
        self.assertEqual(self.select(doc,start=0)[0],400)
        self.assertEqual(self.select(doc,expected_revision=0)[0],409)
        self.assertEqual(self.select(doc,owner_ticket=ticket(1))[0],409)
        self.assertEqual(self.select(doc,'en')[0],200)
        self.assertEqual(self.select(doc,'en')[0],409)

    def test_binary_txt_bom_exact_raw_hash_and_utf8_contract(self):
        import hashlib
        raw=b'\xef\xbb\xbfQuestion 1\nA ballot '+ '🗳?'.encode()
        status,result,_=self.post('/api/intake/upload',raw=raw,headers={'Content-Type':'text/plain','X-Oracle-Intake':json.dumps({'owner_ticket':ticket(),'expected_revision':0})})
        self.assertEqual(status,200);doc=result['document']
        self.assertEqual(doc['raw_sha256'],hashlib.sha256(raw).hexdigest());self.assertEqual(doc['text'],'Question 1\nA ballot 🗳?')
        self.assertEqual(doc['source_locale'],'unknown');self.assertNotEqual(doc['raw_sha256'],doc['text_sha256'])
        self.post('/api/intake/discard',{'prepared_id':result['prepared_id']})
        self.assertEqual(self.post('/api/intake/upload',raw=b'\xffbad',headers={'Content-Type':'text/plain','X-Oracle-Intake':json.dumps({'owner_ticket':ticket(),'expected_revision':0})})[0],415)

    def test_upload_mime_header_and_resource_bounds(self):
        context=json.dumps({'owner_ticket':ticket(),'expected_revision':0})
        self.assertEqual(self.post('/api/intake/upload',raw=b'abc',headers={'Content-Type':'image/png','X-Oracle-Intake':context})[0],415)
        self.assertEqual(self.post('/api/intake/upload',raw=b'abc',headers={'Content-Type':'text/plain'})[0],400)
        self.assertEqual(self.post('/api/intake/upload',raw=b'x'*(256*1024+1),headers={'Content-Type':'text/plain','X-Oracle-Intake':context})[0],413)
        self.assertEqual(self.prepare('x'*80001)[0],413)

    def test_reading_assumption_missing_accented_and_whole_labels(self):
        doc=self.commit();result=self.select(doc)[1]
        self.assertEqual(result['readability']['reason'],'explicit_method_choice_required')
        result=self.select(doc,'en',block_id='whole',owner_ticket=ticket(3))[1]
        self.assertEqual(result['readability']['scope'],'whole_document')
        self.assertEqual(result['quote'],TEXT)

    def test_intake_never_changes_corpus_answer_engine_or_operations_content(self):
        with urlopen(self.origin+'/api/operations') as response: before=json.load(response)
        with urlopen(self.origin+'/api/health') as response: counts=json.load(response)['counts']
        canary='VISITOR_PRIVATE_CANARY_735'
        with patch.object(EvidenceLoop,'answer',side_effect=AssertionError('intake called engine')):
            doc=self.commit('Question 1\n'+canary+' may stay?');self.assertEqual(self.select(doc,'en')[0],200)
        with urlopen(self.origin+'/api/operations') as response: after=json.load(response)
        with urlopen(self.origin+'/api/health') as response: self.assertEqual(json.load(response)['counts'],counts)
        self.assertEqual(before,after);self.assertNotIn(canary,json.dumps(after));self.assertNotIn(self.session,json.dumps(after))

    def test_erase_during_parser_no_late_commit_no_bytes_released(self):
        entered=threading.Event();resume=threading.Event();result=[]
        original=parse_paste
        def blocked(*args,**kwargs):entered.set();resume.wait(3);return original(*args,**kwargs)
        with patch('open_oracle.private_intake.parse_paste',side_effect=blocked):
            worker=threading.Thread(target=lambda:result.append(self.prepare('PRIVATE_UNRELEASED_TEXT')));worker.start()
            try:
                self.assertTrue(entered.wait(2));self.assertEqual(self.post('/api/erase',{})[0],200)
                resume.set();worker.join(3)
                self.assertEqual(result[0][0],410);self.assertNotIn('PRIVATE_UNRELEASED_TEXT',json.dumps(result))
            finally:resume.set();worker.join(3)
        self.assertEqual(self.post('/api/intake/state',{})[0],410)

    def test_global_parser_busy_no_queue_and_discard_free_preview(self):
        entered=threading.Event();resume=threading.Event();result=[];original=parse_paste
        def blocked(*args,**kwargs):entered.set();resume.wait(3);return original(*args,**kwargs)
        with patch('open_oracle.private_intake.parse_paste',side_effect=blocked):
            worker=threading.Thread(target=lambda:result.append(self.prepare()));worker.start()
            try:
                self.assertTrue(entered.wait(2));self.assertEqual(self.post('/api/intake/state',{},session=str(uuid4()))[0],429)
                resume.set();worker.join(3);self.assertEqual(result[0][0],200)
            finally:resume.set();worker.join(3)
        self.assertEqual(self.post('/api/intake/discard',{'prepared_id':result[0][1]['prepared_id']})[0],200)
        self.assertEqual(self.prepare(n=1)[0],200)

    def test_source_commit_discards_running_exact_source_request(self):
        prepared=self.prepare()[1];entered=threading.Event();resume=threading.Event();answers=[]
        original=EvidenceLoop.answer
        def blocked(engine,*args,**kwargs):entered.set();resume.wait(3);return original(engine,*args,**kwargs)
        with patch.object(EvidenceLoop,'answer',blocked):
            worker=threading.Thread(target=lambda:answers.append(self.post('/api/ask',{'question':'What is the COMBAT tax rate?','request_id':'old-request'})));worker.start()
            try:
                self.assertTrue(entered.wait(2))
                status,_,_=self.post('/api/intake/commit',{'prepared_id':prepared['prepared_id'],'owner_ticket':ticket(1),'expected_revision':0})
                self.assertEqual(status,200);resume.set();worker.join(3);self.assertEqual(answers[0][0],410)
                self.assertNotIn('answer',answers[0][1])
            finally:resume.set();worker.join(3)
        self.assertEqual(self.post('/api/ask',{'question':'What is the COMBAT tax rate?','request_id':'fresh'})[1]['status'],'answered')

    def test_text_erase_command_also_drops_intake(self):
        self.commit()
        self.assertEqual(self.post('/api/ask',{'question':'Erase this session'})[0],200)
        self.assertEqual(self.post('/api/intake/state',{})[0],410)

    def test_real_retained_pdf_native_extraction_stays_unverified(self):
        from open_oracle.ballot_intake import PopplerTools
        try: PopplerTools.installed()
        except Exception: self.skipTest('native parser unavailable')
        from open_oracle.corpus import Corpus
        raw=Corpus().originals['jceb-sample'].read_bytes()
        status,result,_=self.post('/api/intake/upload',raw=raw,headers={'Content-Type':'application/pdf','X-Oracle-Intake':json.dumps({'owner_ticket':ticket(),'expected_revision':0})})
        self.assertEqual(status,200,result);self.assertEqual(result['document']['kind'],'pdf')
        self.assertEqual(len(result['document']['pages']),2);self.assertEqual(result['document']['source_locale'],'unknown')
        self.assertFalse(result['document']['original_verified']);self.assertIn('pdf_reading_order_unverified',result['document']['warnings'])


if __name__=='__main__':unittest.main()
