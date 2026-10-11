"""Exact named assets, same CSP, no traversal or directory serving."""
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.request import urlopen
from urllib.error import HTTPError
from open_oracle.server import make_server, public_brand_asset, PUBLIC_BRAND_ASSETS

class PublicBrandTests(unittest.TestCase):
    def test_aliases_are_exact_and_contained(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for route,(relative,mime) in PUBLIC_BRAND_ASSETS.items():
                file=root/relative;file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(route.encode())
            with patch('open_oracle.server.ROOT',root):
                for route,(_,mime) in PUBLIC_BRAND_ASSETS.items():
                    self.assertEqual(public_brand_asset(route),(route.encode(),mime))
                for route in ('/icons/phosphor/', '/icons/phosphor/private.svg','/brand/fonts/../private.ttf','/brand/fonts/LibreBaskerville[wght].ttf'):
                    self.assertIsNone(public_brand_asset(route))
                route='/icons/phosphor/play.svg';file=root/PUBLIC_BRAND_ASSETS[route][0];file.unlink()
                with tempfile.NamedTemporaryFile() as outside:
                    file.symlink_to(outside.name);self.assertIsNone(public_brand_asset(route))

    def test_font_http_security_and_unknown_names(self):
        server=make_server(port=0);worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
        origin=f'http://127.0.0.1:{server.server_port}'
        try:
            for route in ('/brand/fonts/libre-baskerville.ttf','/brand/fonts/libre-franklin.ttf'):
                expected=public_brand_asset(route)[0]
                with urlopen(origin+route,timeout=3) as response:
                    self.assertEqual(response.read(),expected);self.assertEqual(response.headers['Content-Type'],'font/ttf')
                    self.assertEqual(response.headers['Cache-Control'],'no-store');self.assertIn("default-src 'self'",response.headers['Content-Security-Policy'])
            for route in ('/icons/phosphor/','/icons/phosphor/unknown.svg','/brand/fonts/private.ttf'):
                with self.assertRaises(HTTPError) as held:urlopen(origin+route,timeout=3)
                self.assertEqual(held.exception.code,404);held.exception.close()
        finally:server.shutdown();server.server_close();worker.join(3)
