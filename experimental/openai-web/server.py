"""Loopback-only static review server. No inference, microphone or visitor storage."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import json

ROOT = Path(__file__).resolve().parent
FILES = {
    '/': (ROOT / 'web/index.html', 'text/html; charset=utf-8'),
    '/app.mjs': (ROOT / 'web/app.mjs', 'text/javascript; charset=utf-8'),
    '/core.mjs': (ROOT / 'web/core.mjs', 'text/javascript; charset=utf-8'),
    '/style.css': (ROOT / 'web/style.css', 'text/css; charset=utf-8'),
    '/fixture.json': (ROOT / 'fixtures/combat.json', 'application/json'),
    '/logo.svg': (ROOT.parents[1] / 'brand/logos/open-oracle-vote.svg', 'image/svg+xml'),
}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # Never log visitor URLs, question content, headers or identifiers.

    def reply(self, status, data, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Permissions-Policy', 'microphone=(), camera=(), geolocation=()')
        self.send_header('Content-Security-Policy', "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; media-src 'none'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        port = self.server.server_port
        if self.headers.get('Host') not in {f'127.0.0.1:{port}', f'localhost:{port}'}:
            self.reply(403, b'{"error":"loopback_only"}')
            return
        if self.path == '/api/capabilities':
            self.reply(200, json.dumps({'mode': 'fixture', 'providers': 'disabled', 'credentials_read': False, 'microphone': 'disabled', 'visitor_persistence': False}).encode())
        elif self.path in FILES:
            path, mime = FILES[self.path]
            self.reply(200, path.read_bytes(), mime)
        else:
            self.reply(404, b'{"error":"not_found"}')

    def do_POST(self):
        self.close_connection = True
        self.reply(405, b'{"error":"provider_and_intake_routes_disabled"}')


def make_server(port=8894):
    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    server.daemon_threads = True
    return server


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8894)
    args = parser.parse_args()
    server = make_server(args.port)
    print(f'OpenOracle fixture review: http://127.0.0.1:{server.server_port}', flush=True)
    server.serve_forever()
