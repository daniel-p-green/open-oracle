import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server

class MapSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        registry=json.loads((server.ROOT.parents[1]/'docs/rebuild/MAP-SOURCE-MANIFEST.json').read_text())
        self.data={'version':1,'projection':'EPSG:5070','sources':registry['sources']}
        self.write()
    def tearDown(self):self.temp.cleanup()
    def write(self):
        self.raw=json.dumps(self.data).encode();(self.root/'maps.json').write_bytes(self.raw)
        self.receipt={'sha256':hashlib.sha256(self.raw).hexdigest(),'source_hashes_verified':4,'districts_per_plan':[8,8],'original_and_projected_geometry_valid':True}
        (self.root/'receipt.json').write_text(json.dumps(self.receipt))
    def test_forged_derivative_with_copied_source_metadata_and_self_matching_receipt_is_rejected(self):
        # This payload/receipt passed before the independent application pin.
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(),self.receipt['sha256'])
        with self.assertRaisesRegex(ValueError,'map_integrity'):server.load_maps(self.root)
    def test_symlink_outside_review_directory_is_not_served(self):
        (self.root/'maps.json').unlink();(self.root/'maps.json').symlink_to(server.ROOT/'fixtures/combat.json')
        with self.assertRaises(ValueError):server.load_maps(self.root)
