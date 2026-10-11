"""Offline parser, strict index and citation contracts; no query embeddings.

Retained document vectors test document self similarity. Saved query evidence
supports only an ordinal projection, never reconstructed query scores.
"""
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from open_oracle.corpus import Corpus
from strands_quality.research_corpus import Registry, Source, Scope, _chunks, digest, load_verified_corpus
from strands_quality.semantic_retrieval import LocalVectorBackend, S3VectorBackend, fingerprint, binding
from strands_quality.semantic_errors import SemanticUnavailable

PROJECT = Path(__file__).resolve().parents[1]
TARGET = 'combat:jceb-sample:8998:4a50da630896'
TRUST = 'combat:jceb-sample:9422:0612fe0d2d60'
CONTROL = 'combat:jceb-sample:9593:c1bd2c807f9a'


class RetainedDocumentEncoder:
    """Only reads existing document vectors. Unknown/query strings are fatal."""
    def __init__(self, registry, artifact):
        self.revision = artifact['manifest']['encoder_revision']
        self.lookup = {registry.chunks[k].text: v for k, v in artifact['vectors'].items()}
        self.calls = []
    def embed(self, text):
        if text not in self.lookup:
            raise AssertionError('Offline review cannot recreate a query embedding')
        self.calls.append(text)
        return self.lookup[text]


class StructuralRetrievalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = load_verified_corpus(Corpus())
        path = PROJECT/'.local/semantic/titan-public-combat-three-chunk-vectors.json'
        cls.artifact = json.loads(path.read_text()) if path.exists() else None

    def synthetic(self, text, *, role='ballot_proposal', quality='verified_reading_copy'):
        directory = TemporaryDirectory(); self.addCleanup(directory.cleanup)
        original = Path(directory.name)/'public.txt'; original.write_text(text)
        source = Source('held-out', 'Official fixture', 'https://example.gov/ballot', 'issuer', role,
                        original, digest(original.read_bytes()), text, digest(text.encode()),
                        'synthetic_parser_contract', authority='JCEB', quality=quality)
        chunks = _chunks(source, text, 0, {'id':'unseen-measure','scope':'countywide'}, 'public question')
        return Registry([source], chunks)

    def backend(self, artifact=None, check=lambda: None):
        if self.artifact is None:
            self.skipTest('Retained local public vectors absent; no regeneration permitted')
        registry = Registry(list(self.base.sources.values()), list(self.base.chunks.values()))
        artifact = artifact or deepcopy(self.artifact)
        encoder = RetainedDocumentEncoder(registry, artifact)
        backend = LocalVectorBackend(registry, artifact, encoder, check=check)
        registry.semantic_backend = backend
        candidates = tuple(c for c in registry.chunks.values()
                           if registry.eligible(c, Scope(), 'combat', 'ballot_fact'))
        return registry, encoder, backend, candidates

    def signed(self, artifact):
        artifact['manifest_sha256'] = fingerprint(artifact['manifest'])
        artifact['artifact_sha256'] = fingerprint({k:artifact[k] for k in ('manifest','manifest_sha256','vectors')})
        return artifact

    def test_actual_corpus_generic_controls_and_6096_preserved(self):
        controls = [c for c in self.base.chunks.values() if c.chunk_type == 'ballot_choice_controls']
        self.assertEqual(len(controls), 16)
        self.assertEqual(sum(c.source_id == 'jceb-sample' for c in controls), 10)
        self.assertEqual(sum(c.source_id == 'kceb-sample' for c in controls), 6)
        self.assertGreater(len({c.contest_id for c in controls if c.contest_id != 'combat'}), 1)
        self.assertTrue(all(self.base.sources[c.source_id].text[c.start:c.end] == c.text
                            and digest(c.text.encode()) == c.sha256 for c in self.base.chunks.values()))
        # The separately appended ordinance loader must survive this patch.
        if 'combat-6096-selected-v1' in self.base.sources:
            chunks = [c for c in self.base.chunks.values() if c.source_id == 'combat-6096-selected-v1']
            self.assertEqual(len(chunks), 8)
            self.assertTrue(all(c.chunk_type == 'content' for c in chunks))
            self.assertTrue(all(not self.base.eligible(c,Scope(),'combat','ballot_fact') for c in chunks))

    def test_held_out_layout_options_and_short_substantive_content(self):
        for pair in ('YES\nNO', 'YES NO', 'NO  YES', 'FOR\nAGAINST', 'AGAINST\nFOR'):
            with self.subTest(pair=pair):
                registry = self.synthetic('Shall the district renew for ten years?\n'+pair)
                self.assertEqual(list(registry.chunks.values())[-1].chunk_type, 'ballot_choice_controls')
        registry = self.synthetic('Shall the district renew?\nTen years.')
        self.assertTrue(all(c.chunk_type == 'content' for c in registry.chunks.values()))
        native = self.synthetic('Shall this pass?\nYES NO',quality='native_html')
        self.assertEqual(list(native.chunks.values())[-1].chunk_type,'ballot_choice_controls')

    def test_negative_ambiguous_or_unverified_forms_remain_content(self):
        for tail in ('NO.', 'yes\nno', 'YES\nYES', 'YES / NO',
                     'A YES vote renews; a NO vote ends the tax.', '"YES\nNO"',
                     'YES\nNO\nThis paragraph defines the consequences.'):
            with self.subTest(tail=tail):
                self.assertTrue(all(c.chunk_type == 'content' for c in
                    self.synthetic('Shall this pass?\n'+tail).chunks.values()))
        for role, quality in (('current_law','verified_reading_copy'),
                              ('adopted_proposal','verified_reading_copy'),
                              ('ballot_proposal','unverified_extraction')):
            self.assertTrue(all(c.chunk_type == 'content' for c in
                self.synthetic('Shall this pass?\nYES\nNO',role=role,quality=quality).chunks.values()))
        self.assertTrue(all(c.chunk_type == 'content' for c in self.synthetic('YES\nNO').chunks.values()))

    def test_structural_read_lexical_original_available_but_claim_citation_forbidden(self):
        registry = self.synthetic('Shall this pass?\nFOR  \nAGAINST')
        control = list(registry.chunks.values())[-1]
        self.assertEqual(registry.read(control.id)['text'], 'FOR  \nAGAINST')
        self.assertGreaterEqual(len(control.text),12)  # would pass citation length alone
        self.assertFalse(registry.read(control.id)['factual_claim_citation_eligible'])
        self.assertIn(control.id, [r['chunk_id'] for r in registry.rank('AGAINST',Scope(),'unseen-measure','ballot_fact')])
        self.assertTrue(registry.acquire(control.source_id)['original_sha256'])
        with self.assertRaisesRegex(ValueError, 'Structural ballot controls'):
            registry.citation(control.id, control.text)
        source = list(registry.sources.values())[0]
        forged = replace(list(registry.chunks.values())[0],chunk_type='ballot_choice_controls')
        with self.assertRaisesRegex(ValueError, 'literal layout'):
            Registry([source],[forged])

    def test_actual_sdk_read_controls_inspectable_without_issued_claim_span(self):
        from test_research import ResearchModel
        from strands_quality.research_agent import ResearchRequest
        registry = self.synthetic('Shall this pass?\nFOR  \nAGAINST')
        request = ResearchRequest(registry, scope=Scope(), model=ResearchModel(), execution='synthetic_sdk')
        def call(name, **kwargs):
            result = getattr(request.agent.tool, name)(**kwargs)
            self.assertEqual(result['status'], 'success')
            return json.loads(result['content'][0]['text'])
        call('plan_evidence', contest_id='unseen-measure', parts=[
            {'id':'part', 'question':'Which options are printed?', 'query':'AGAINST', 'purpose':'ballot_fact'}])
        call('search_official_sources', part_id='part')
        call('acquire_official_source', source_id='held-out')
        call('search_indexed_evidence', part_id='part')
        control = list(registry.chunks.values())[-1]
        value = call('read_evidence_chunk', part_id='part', chunk_id=control.id)
        self.assertEqual(value['text'],control.text)
        self.assertEqual(value['chunk_type'],'ballot_choice_controls')
        self.assertFalse(value['factual_claim_citation_eligible'])
        self.assertEqual(value['citation_spans'],[])
        self.assertEqual(request.citation_spans,{})
        old = next(c for c in self.base.chunks.values() if c.source_id == 'combat-6096')
        self.assertFalse(self.base.read(old.id)['factual_claim_citation_eligible'])

    def test_retained_document_self_similarity_content_only(self):
        registry, encoder, backend, candidates = self.backend()
        self.assertEqual(len(candidates),3)
        for ident in (TARGET, TRUST):
            order = backend.rank(registry.chunks[ident].text, candidates)
            self.assertEqual(order[0],ident)
            self.assertEqual(set(order),{TARGET,TRUST})
            self.assertNotIn(CONTROL,order)
            self.assertEqual(registry.citation(ident,registry.chunks[ident].text)['chunk_sha256'],registry.chunks[ident].sha256)
        self.assertEqual(len(encoder.calls),2)  # local lookup only

    def test_missing_control_and_missing_content_both_fallback_before_lookup(self):
        if self.artifact is None: self.skipTest('Retained local public vectors absent')
        for ident in (CONTROL,TARGET):
            artifact = deepcopy(self.artifact)
            artifact['manifest']['records'] = [r for r in artifact['manifest']['records'] if r['chunk_id'] != ident]
            del artifact['vectors'][ident]
            registry,encoder,_,_ = self.backend(self.signed(artifact))
            rows = registry.rank('quarter cent',Scope(),'combat','ballot_fact')
            self.assertTrue(rows)
            self.assertEqual(rows.semantic_status,'unavailable')
            self.assertEqual(encoder.calls,[])

    def test_stale_control_and_cancellation_fatal_before_lookup(self):
        if self.artifact is None: self.skipTest('Retained local public vectors absent')
        artifact = deepcopy(self.artifact)
        next(r for r in artifact['manifest']['records'] if r['chunk_id'] == CONTROL)['end'] += 1
        _,encoder,backend,candidates = self.backend(self.signed(artifact))
        with self.assertRaisesRegex(ValueError,'Stale vector'):
            backend.rank('unembedded query',candidates)
        self.assertEqual(encoder.calls,[])
        def cancel(): raise RuntimeError('request cancelled')
        registry,encoder,_,_ = self.backend(check=cancel)
        with self.assertRaisesRegex(RuntimeError,'cancelled'):
            registry.rank('quarter cent',Scope(),'combat','ballot_fact')
        self.assertEqual(encoder.calls,[])

    def test_control_only_validated_without_lookup_and_scope_filters_precede_backend(self):
        registry,encoder,backend,_ = self.backend()
        self.assertEqual(backend.rank('unknown query',(registry.chunks[CONTROL],)),[])
        for scope in (Scope(authority='KCEB'),Scope(state='KS'),Scope(election_date='2024-11-05'),
                      Scope(versions=(('jceb-sample','0'*64),))):
            rows = registry.rank('quarter cent',scope,'combat','ballot_fact',source_ids={'jceb-sample'})
            self.assertEqual(rows,[])
        self.assertEqual(encoder.calls,[])

    def test_s3_simulation_filters_content_after_full_validation(self):
        registry,encoder,_,candidates = self.backend()
        class FakeIndex:
            def __init__(self): self.calls=[]
            def query_vectors(self,**kwargs): self.calls.append(kwargs); return {'vectors':[]}
        client = FakeIndex()
        backend = S3VectorBackend(registry,self.artifact,encoder,client=client,
            index_arn='arn:aws:s3vectors:us-east-1:123456789012:bucket/staged/index/staged')
        backend.rank(registry.chunks[TARGET].text,candidates)
        request = client.calls[0]
        allowed = request['filter']['$and'][1]['binding_sha256']['$in']
        self.assertEqual(set(allowed),{fingerprint(binding(registry,registry.chunks[k])) for k in (TARGET,TRUST)})
        self.assertEqual(request['topK'],2)
        with self.assertRaisesRegex(ValueError,'Unbound cloud vector'):
            client.query_vectors = lambda **_: {'vectors':[{'key':fingerprint(binding(registry,registry.chunks[CONTROL]))}]}
            backend.rank(registry.chunks[TARGET].text,candidates)

    def test_historical_query_ordinal_projection_only(self):
        path = PROJECT/'evals/semantic-research-http-20261011/complete-application.json'
        if not path.exists(): self.skipTest('Retained historical receipt absent')
        saved = json.loads(path.read_text())
        attempts = saved['trials'][0]['semantic_attempts']
        orders = [a['ranked_ids'] for a in attempts if a.get('status') == 'semantic_used']
        self.assertTrue(orders)
        for order in orders:
            self.assertEqual(order,[CONTROL,TARGET,TRUST])
            projected = [k for k in order if self.base.chunks[k].chunk_type == 'content']
            self.assertEqual(projected,[TARGET,TRUST])
        self.assertFalse(saved['query_vectors_retained'])
        self.assertEqual(self.base.rank('How long would renewal last?',Scope(),'combat','ballot_fact'),[])


if __name__ == '__main__': unittest.main()
