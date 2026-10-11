from pathlib import Path
from tempfile import TemporaryDirectory
import shutil, unittest
from open_oracle.corpus import Corpus
from strands_quality.research_corpus import Registry, Scope, load_verified_corpus
from strands_quality.chapter93 import load_chapter93, SOURCE_ID

ARCHIVE=Path(__file__).resolve().parents[1]/'.local/sources/county-code-chapter-93'
class Chapter93Tests(unittest.TestCase):
    def test_complete_native_document_is_three_exact_pages(self):
        source,chunks=load_chapter93(ARCHIVE)
        self.assertEqual([c.page for c in chunks],[1,2,3])
        self.assertEqual(source.role,'historical_law')
        self.assertIn('December 11, 2018',source.text)
        self.assertIn('currency unverified',source.title)
        for c in chunks:self.assertEqual(c.text,source.text[c.start:c.end])

    def test_explicit_index_allows_reference_but_not_current_law(self):
        registry=load_verified_corpus(Corpus(),county_code_archive=ARCHIVE)
        self.assertEqual(len(registry.sources),6)
        self.assertTrue(registry.rank('trust fund',Scope(),'combat','legal_reference',source_ids={SOURCE_ID}))
        for purpose in ['ballot_fact','current_law','prediction','voting_procedure']:
            self.assertEqual(registry.rank('tax',Scope(),'combat',purpose,source_ids={SOURCE_ID}),[])
        self.assertNotIn(SOURCE_ID,load_verified_corpus(Corpus()).sources)

    def test_bytes_extraction_and_later_acquisition_drift_fail(self):
        for name in ['chapter-93.pdf','chapter-93.txt']:
            with TemporaryDirectory() as tmp:
                root=Path(tmp);shutil.copytree(ARCHIVE,root,dirs_exist_ok=True)
                sources,chunks=load_chapter93(root);registry=Registry([sources],chunks)
                (root/name).write_bytes(b'changed')
                with self.assertRaises(ValueError):load_chapter93(root)
                if name.endswith('.pdf'):
                    with self.assertRaises(ValueError):registry.read(chunks[0].id)

    def test_original_rate_units_and_expiration_not_spliced_into_ballot(self):
        source,chunks=load_chapter93(ARCHIVE)
        self.assertIn('one-quarter of one percent',chunks[0].text)
        self.assertIn('shall automatically terminate March 31, 2027',chunks[2].text)
        self.assertNotIn('March 31, 2037',source.text)
        self.assertIn('authorized in the County’s annual budget',chunks[0].text)

if __name__=='__main__':unittest.main()
