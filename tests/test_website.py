"""Local presentation routes cannot imply intake or weaken source fidelity."""
import json
import threading
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from open_oracle.server import make_server
from open_oracle.corpus import Corpus

class RetainedWording(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_quote=False; self.parts=[]
    def handle_starttag(self, tag, attrs):
        if tag=='blockquote' and dict(attrs).get('id')=='retained-wording':self.in_quote=True
    def handle_endtag(self, tag):
        if tag=='blockquote':self.in_quote=False
    def handle_data(self, data):
        if self.in_quote:self.parts.append(data)

class WebsiteTests(unittest.TestCase):
    def test_complete_original_survives_markup_and_exactly_two_clauses_are_marked(self):
        html=(Path(__file__).resolve().parents[1]/'web/website.html').read_text()
        parser=RetainedWording();parser.feed(html)
        self.assertEqual(''.join(parser.parts),Corpus().evidence['combat:jceb-sample']['text'])
        self.assertEqual(html.count('<u>'),2)
        self.assertIn('Checking private local intake availability.',html)
        self.assertIn('Upload PDF or UTF-8 TXT',html)
        self.assertIn('/intake.js',html)
        # The landing owner can simplify copy while keeping truthful capability limits.
        status = html.split('id="evaluator-status"', 1)[1].split('</p>', 1)[0]
        self.assertRegex(status, r'(?i)uploaded wording.*unverified')
        self.assertRegex(status, r'(?i)AI explanations?.*translation.*not connected')

    def test_additive_static_routes_keep_security_and_existing_surfaces(self):
        server=make_server(port=0,operations=True)
        worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
        url='http://127.0.0.1:'+str(server.server_port)
        try:
            for path,mime in (('/website','text/html'),('/website.css','text/css'),('/website.js','text/javascript'),('/intake.js','text/javascript'),
                              ('/','text/html'),('/copilot','text/html'),('/devices','text/html')):
                with urlopen(url+path,timeout=3) as response:
                    self.assertEqual(response.status,200)
                    self.assertTrue(response.headers['Content-Type'].startswith(mime))
                    self.assertEqual(response.headers['Cache-Control'],'no-store')
                    self.assertIn("default-src 'self'",response.headers['Content-Security-Policy'])
                    self.assertEqual(response.headers['X-Content-Type-Options'],'nosniff')
            with self.assertRaises(HTTPError) as error:
                urlopen(Request(url+'/website',headers={'Host':'untrusted.example'}),timeout=3)
            self.assertEqual(error.exception.code,403);error.exception.close()
            with self.assertRaises(HTTPError) as error:
                urlopen(url+'/api/ballot/evaluate',timeout=3)
            self.assertEqual(error.exception.code,404);error.exception.close()
            with urlopen(url+'/api/operations',timeout=3) as response:
                self.assertNotIn('completed_operations',json.load(response)['totals'])
        finally:
            server.shutdown();server.server_close();worker.join(timeout=2)
