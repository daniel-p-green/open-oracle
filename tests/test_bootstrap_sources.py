from pathlib import Path
import tempfile
import unittest
from open_oracle.bootstrap_sources import install,read_bound,collect
from open_oracle.corpus import Corpus
from strands_quality.research_corpus import load_verified_corpus

class BootstrapTests(unittest.TestCase):
    def test_pinned_subset_reconstructs_both_authorities_without_overwrite(self):
        source=Corpus().research
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'.gitignore').write_text('research/HackMidwest2026_research/\n.local/\n')
            proof=install(source,checkout=root)
            self.assertEqual(proof['network_calls'],0);self.assertEqual(proof['model_calls'],0)
            c=Corpus(root/'research/HackMidwest2026_research');self.assertEqual(c.counts()['contests'],55)
            self.assertEqual(set(load_verified_corpus(c).sources),{'jceb-sample','kceb-sample','rsmo-67.547','combat-6096'})
            self.assertFalse((root/'research/HackMidwest2026_research/START-HERE.md').exists())
            with self.assertRaises(ValueError):install(source,checkout=root)
    def test_bad_pin_path_escape_and_symlink_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'x').write_text('public fixture')
            with self.assertRaises(ValueError):read_bound(root,'x','0'*64)
            (root/'link').symlink_to(root/'x')
            with self.assertRaises(ValueError):read_bound(root,'link')
            with self.assertRaises(ValueError):read_bound(root,'../outside')
    def test_check_only_writes_nothing_and_refuses_unignored_archive(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'.gitignore').write_text('research/HackMidwest2026_research/\n.local/\n')
            proof=install(Corpus().research,checkout=root,check_only=True)
            self.assertFalse(proof['copied']);self.assertEqual(list(root.iterdir()),[root/'.gitignore'])
            (root/'.gitignore').write_text('')
            with self.assertRaises(ValueError):install(Corpus().research,checkout=root)
if __name__=='__main__':unittest.main()
