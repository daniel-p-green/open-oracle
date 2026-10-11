import copy, tempfile, unittest, http.client, json, threading
from pathlib import Path
from unittest.mock import patch
from open_oracle.corpus import Corpus
from open_oracle.claim_bindings import fingerprint
from open_oracle.render_catalog import rendering_catalog, CatalogUnavailable

class RenderCatalogTests(unittest.TestCase):
    def setUp(self): self.corpus = Corpus()
    def test_full_finite_cards_sources_and_fingerprints(self):
        catalog=rendering_catalog(self.corpus, {'authority':'KCEB'})
        self.assertEqual(set(catalog), {'sources','contests','cards','source_bindings','official_links','candidate_sources'})
        self.assertEqual(len(catalog['cards']['combat-explanation-v1']['facets']),5)
        self.assertEqual(len(catalog['cards']['amendment-7-explanation-v1']['facets']),5)
        for ident,source in catalog['sources'].items(): self.assertEqual(catalog['source_bindings'][ident],fingerprint(source))
        for card in catalog['cards'].values():
            for facet in card.get('facets',[]):
                source=catalog['sources'][facet['evidence_id']]
                self.assertEqual(source['text'][facet['start']:facet['end']],facet['quote'])
        self.assertIn('atlarge-1-property-v1',catalog['cards'])
    def test_authority_specific_amendment_card_cannot_cross_board(self):
        for authority, source_id in [('KCEB','kceb-sample'),('JCEB','jceb-sample')]:
            catalog=rendering_catalog(self.corpus, {'authority':authority})
            self.assertEqual(catalog['cards']['amendment-7-explanation-v1']['evidence_id'],'amendment-7:'+source_id)
            self.assertNotIn('amendment-7:'+('jceb-sample' if authority=='KCEB' else 'kceb-sample'),catalog['sources'])
    def test_unknown_or_historical_scope_rejects(self):
        for scope in [{'election_date':'2024-11-05'},{'authority':'KS'},{'_comparison_topic':'property'},{'district':True}]:
            with self.assertRaises(ValueError): rendering_catalog(self.corpus,scope)
    def test_source_or_contest_mutation_rejects_before_bootstrap(self):
        self.corpus.evidence['combat:jceb-sample']['text']='altered'
        with self.assertRaises(CatalogUnavailable): rendering_catalog(self.corpus)
        self.corpus=Corpus(); self.corpus.contests['combat']['title']='altered'
        with self.assertRaises(CatalogUnavailable): rendering_catalog(self.corpus)
    def test_changed_original_after_startup_rejects(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'changed.pdf';path.write_bytes(b'changed')
            self.corpus.originals['jceb-sample']=path
            with self.assertRaises(CatalogUnavailable): rendering_catalog(self.corpus)
    def test_missing_proposal_or_attributed_archive_rejects(self):
        with patch('open_oracle.amendment7.original_pdf',return_value=None):
            with self.assertRaises(CatalogUnavailable): rendering_catalog(self.corpus)
        with patch('open_oracle.amendment7.fair_original',return_value=None):
            with self.assertRaises(CatalogUnavailable): rendering_catalog(self.corpus)
        with patch('open_oracle.demo_sources.original_text',return_value=None):
            with self.assertRaises(CatalogUnavailable): rendering_catalog(self.corpus)
    def test_return_is_isolated_and_has_no_receipts_aliases_or_controller(self):
        catalog=rendering_catalog(self.corpus)
        catalog['sources']['combat:jceb-sample']['text']='caller mutation'
        self.assertNotEqual(self.corpus.evidence['combat:jceb-sample']['text'],'caller mutation')
        for contest in catalog['contests'].values():self.assertNotIn('aliases',contest)
        self.assertFalse(set(catalog)&{'review','receipt','speech','request_id','session_id','release_id'})

class RenderCatalogHTTPTests(unittest.TestCase):
    def test_actual_scope_cache_origin_and_changed_source_guards(self):
        from open_oracle.server import make_server
        corpus=Corpus();server=make_server(port=0,corpus=corpus)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        conn=http.client.HTTPConnection('127.0.0.1',server.server_port,timeout=5)
        def get(path,headers=None):
            conn.request('GET',path,headers=headers or {});response=conn.getresponse()
            return response.status,dict(response.getheaders()),json.loads(response.read())
        try:
            status,headers,catalog=get('/api/render-catalog?authority=unknown&election_date=2026-11-03')
            self.assertEqual(status,200);self.assertEqual(headers['Cache-Control'],'no-store')
            self.assertEqual(catalog,rendering_catalog(corpus,{'authority':'unknown','election_date':'2026-11-03'}))
            for query in ['authority=KS','authority=KCEB&authority=JCEB','election_date=2024-11-05','_comparison_topic=property','broken','authority=']:
                self.assertEqual(get('/api/render-catalog?'+query)[0],400)
            self.assertEqual(get('/api/render-catalog',{'Origin':'http://foreign.invalid'})[0],403)
            self.assertEqual(get('/api/render-catalog',{'Host':'foreign.invalid'})[0],403)
            health=get('/api/health')[2];self.assertEqual(health['mode'],'exact_source')
            self.assertEqual(health['voice'],'not_connected');self.assertEqual(health['voice_sessions_remaining'],0)
            corpus.evidence['combat:jceb-sample']['text']='changed after startup'
            status,_,body=get('/api/render-catalog')
            self.assertEqual(status,503);self.assertNotIn('changed after startup',json.dumps(body))
        finally:
            conn.close();server.shutdown();server.server_close();thread.join()

if __name__=='__main__':unittest.main()
