"""Optional service wiring with authored vectors and actual Strands SDK, no inference."""
from unittest import TestCase
from threading import Event
from open_oracle.corpus import Corpus
from open_oracle.research import research_private
from open_oracle.research_release import research_reviewed
from open_oracle.research_engine import ResearchEvidenceLoop
from strands_quality.research_agent import ResearchRequest
from strands_quality.research_corpus import Scope, load_verified_corpus
from strands_quality.semantic_retrieval import EmbeddingConfig, LocalVectorBackend, public_manifest, ingest_local
from test_semantic_retrieval import FixtureEncoder
from test_research import ResearchModel
from test_research_release import BoundModel, Review

class SemanticServiceTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=load_verified_corpus(Corpus());cls.config=EmbeddingConfig()
        approved={s.id:s.original_sha256 for s in cls.base.sources.values() if s.quality in {'verified_reading_copy','native_html'}}
        cls.manifest=public_manifest(cls.base,approved,cls.config)
        cls.target=next(c for c in cls.base.chunks.values() if c.source_id=='jceb-sample' and c.contest_id=='combat' and 'ten years' in c.text)
        cls.artifact=ingest_local(cls.base,cls.manifest,FixtureEncoder(cls.config,cls.target.text))
    def factory(self,registries):
        def make(registry,check):
            registries.append(registry)
            return LocalVectorBackend(registry,self.artifact,FixtureEncoder(self.config,self.target.text),check=check)
        return make
    def test_private_calls_get_distinct_registries_and_keep_drafts_private(self):
        registries=[]
        for _ in range(2):
            r=research_private('What is the COMBAT rate and how long does it last?',authority='JCEB',model=ResearchModel(),execution='synthetic_sdk',semantic_backend_factory=self.factory(registries))
            self.assertEqual(r['retrieval'],'fts5_plus_configured_rank_fusion');self.assertFalse(r['public_display']);self.assertFalse(r['speech']);self.assertEqual(len(r['claims']),2)
        self.assertIsNot(registries[0],registries[1])
    def test_reviewed_service_and_browser_engine_keep_independent_release(self):
        registries=[];review=Review()
        r=research_reviewed('What is the COMBAT rate and how long does it last?',authority='JCEB',model=BoundModel(),execution='synthetic_sdk',reviewer=review,semantic_backend_factory=self.factory(registries))
        self.assertTrue(r['public_display']);self.assertFalse(r['speech']);self.assertEqual(review.calls,1);self.assertEqual(len(r['claims']),2)
        engine=ResearchEvidenceLoop(Corpus(),BoundModel,Review(),execution='synthetic_sdk',semantic_backend_factory=self.factory(registries))
        displayed=engine.answer('What is the COMBAT rate and how long does it last?',scope={'authority':'JCEB'})
        self.assertEqual(displayed['status'],'answered');self.assertEqual(displayed['fact_validation']['status'],'supported');self.assertFalse(displayed['speech'])
    def test_factory_revision_changes_receipt_and_cancellation_is_bound(self):
        reg=load_verified_corpus(Corpus());r=ResearchRequest(reg,scope=Scope(),model=ResearchModel(),execution='synthetic_sdk')
        signal=Event();other=ResearchRequest(load_verified_corpus(Corpus()),scope=Scope(),model=ResearchModel(),execution='synthetic_sdk',cancel=signal,semantic_backend_factory=self.factory([]))
        self.assertNotEqual(r.receipt.config_hash,other.receipt.config_hash)
        signal.set()
        with self.assertRaises(TimeoutError):other.registry.rank('quarter cent',Scope(),'combat','ballot_fact')
    def test_wrong_registry_or_nonlocal_backend_cannot_enter_service(self):
        foreign=LocalVectorBackend(self.base,self.artifact,FixtureEncoder(self.config,self.target.text))
        for factory in [lambda *_:foreign,lambda *_:object()]:
            with self.assertRaisesRegex(ValueError,'bind this request registry'):
                research_private('COMBAT',authority='JCEB',model=ResearchModel(),execution='synthetic_sdk',semantic_backend_factory=factory)
    def test_default_remains_lexical_and_rejected_review_keeps_vectors_private(self):
        r=research_private('What is the COMBAT rate and how long does it last?',authority='JCEB',model=ResearchModel(),execution='synthetic_sdk')
        self.assertEqual(r['retrieval'],'sqlite_fts5_bm25');self.assertEqual(r['semantic_backend'],'not_run')
        class Reject(Review):
            def review(self,e):return {'status':'rejected','execution':'offline_stub'}
        r=research_reviewed('What is the COMBAT rate and how long does it last?',authority='JCEB',model=BoundModel(),execution='synthetic_sdk',reviewer=Reject(),semantic_backend_factory=self.factory([]))
        self.assertFalse(r['public_display']);self.assertEqual(r['claims'],[]);self.assertEqual(r['evidence'],[])

    def test_public_search_hints_bind_prompt_revision_without_widening_release(self):
        from strands_quality.semantic_retrieval import PublicSearchHint
        from open_oracle.research_release import requested_parts
        hint=PublicSearchHint('combat','ballot_fact','duration','How long would renewal last?')
        def make(hints):
            reg=load_verified_corpus(Corpus())
            return ResearchRequest(reg,scope=Scope(),model=ResearchModel(),execution='synthetic_sdk',
                semantic_backend_factory=lambda r,c: LocalVectorBackend(r,self.artifact,FixtureEncoder(self.config,self.target.text),check=c,search_hints=hints))
        request=make([hint]);default=make([])
        import json
        context=json.loads(request.prompt('What is the COMBAT duration?'))['application_context']
        self.assertEqual(context['approved_public_search_queries'],[hint.descriptor()])
        self.assertNotIn('approved_public_search_queries',json.loads(default.prompt('What is the COMBAT duration?'))['application_context'])
        self.assertNotEqual(request.receipt.config_hash,default.receipt.config_hash)
        self.assertNotEqual(request.registry.semantic_backend.revision,default.registry.semantic_backend.revision)
        with self.assertRaises(ValueError):requested_parts('How long would COMBAT renewal last?')
        with self.assertRaises(ValueError):PublicSearchHint('combat','prediction','duration',hint.query)
        with self.assertRaises(ValueError):LocalVectorBackend(self.base,self.artifact,FixtureEncoder(self.config),search_hints=[{'query':hint.query}])

    def test_http_factory_is_opt_in_and_passed_to_research_engine(self):
        from unittest.mock import patch
        from open_oracle.server import make_server
        factory=self.factory([])
        with self.assertRaisesRegex(ValueError,'explicitly capped research'):
            make_server(port=0,semantic_backend_factory=factory)
        with patch('open_oracle.openai_integrations.require_live_authorization'), patch('open_oracle.research_engine.build_research_engine') as build:
            server=make_server(port=0,live=True,research=True,max_live_requests=2,semantic_backend_factory=factory)
            try:self.assertIs(build.call_args.kwargs['semantic_backend_factory'],factory)
            finally:server.server_close()
