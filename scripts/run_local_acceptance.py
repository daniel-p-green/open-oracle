"""Read-only loopback health checks or an owned exact-source browser acceptance run.

Never enables provider, sensor or device capture. No package installation or SSH.
"""
import argparse
import hashlib
import json
from pathlib import Path
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import urllib.error
import urllib.request

HASHES = {
    'jceb-sample': '032814e650dbdbdb0064acb396ead6f51dcd087778240802eb6c30c7a5ef64a2',
    'kceb-sample': '92cda731c864b5a84062322a32f743597bcace6f986af4c0e2bfe55c7405dc62',
}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, new_url):
        raise ValueError('Redirects are forbidden in the local acceptance check')


def check_http(url):
    if not re.fullmatch(r'http://127\.0\.0\.1:([0-9]{1,5})', url):
        raise ValueError('Use an exact IPv4 loopback origin, without a path')
    if not 1024 <= int(url.rsplit(':', 1)[1]) <= 65535:
        raise ValueError('Use an unprivileged valid port')
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())

    def get(path, headers=None):
        request = urllib.request.Request(url + path, headers=headers or {}, method='GET')
        try:
            with opener.open(request, timeout=5) as response:
                return response.status, dict(response.headers), response.read(2_000_001)
        except urllib.error.HTTPError as error:
            return error.code, dict(error.headers), error.read(2048)

    status, _, body = get('/api/health')
    if status != 200:
        raise RuntimeError('Local health route did not return 200')
    health = json.loads(body)
    expected = {'status': 'ready', 'mode': 'exact_source', 'provider': None,
                'independent_review': 'not_run', 'voice': 'not_connected',
                'voice_session_available': False, 'election_date': '2026-11-03'}
    if any(health.get(key) != value for key, value in expected.items()):
        raise RuntimeError('Server is not the safe exact-source/voice-off baseline')
    if health.get('input_events', {}).get('enabled') is not False:
        raise RuntimeError('Expected disabled sensor input for this baseline')
    if health.get('source_integrity') != {key: True for key in HASHES}:
        raise RuntimeError('Retained original integrity is not confirmed')
    routes = ('/', '/copilot', '/devices', '/app.js', '/interaction.js',
              '/input-bridge.js', '/live.js', '/devices.js', '/styles.css', '/orb.js')
    for path in routes:
        code, headers, body = get(path)
        if code != 200 or not body or len(body) > 2_000_000:
            raise RuntimeError(f'Asset route failed: {path}')
        if headers.get('Cache-Control') != 'no-store':
            raise RuntimeError(f'Unexpected visitor-content cache policy: {path}')
    originals = {}
    for source, expected_hash in HASHES.items():
        code, headers, body = get('/api/original/' + source)
        actual_hash = hashlib.sha256(body).hexdigest()
        if code != 200 or not body.startswith(b'%PDF-') or actual_hash != expected_hash:
            raise RuntimeError(f'Retained PDF check failed: {source}')
        originals[source] = {'bytes': len(body), 'sha256': actual_hash}
    if get('/api/health', {'Host': 'unexpected.invalid'})[0] != 403:
        raise RuntimeError('Unexpected Host was not rejected')
    if get('/api/health', {'Origin': 'http://unexpected.invalid'})[0] != 403:
        raise RuntimeError('Foreign Origin was not rejected')
    if get('/api/input-events')[0] != 404:
        raise RuntimeError('Default sensor endpoint should be unavailable')
    return {'passed': True, 'execution': 'read_only_actual_loopback_http',
            'url': url, 'health': health, 'originals': originals,
            'host_origin_guards': True, 'get_only': True,
            'physical_capture': False, 'provider_requests': 0,
            'physical_pi': False, 'secure_context_browser_proof': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-running', metavar='LOOPBACK_ORIGIN',
                        help='GET-only check; never launches browser, queries or server')
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path,
                        help='New evidence directory for the isolated offline browser run')
    args = parser.parse_args()
    if args.check_running:
        print(json.dumps(check_http(args.check_running), indent=2))
        return
    repo = args.repo.resolve()
    python = repo / '.venv/bin/python'
    browser_script = Path(__file__).with_name('offline_browser_acceptance.cjs')
    prerequisites = [python, browser_script,
        Path('/opt/homebrew/lib/node_modules/promptfoo/node_modules/playwright'),
        Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')]
    if any(not path.exists() for path in prerequisites) or not shutil.which('node'):
        raise RuntimeError('Missing existing Mac Python/Node/Playwright/Chrome prerequisite; no installation attempted')
    if args.output:
        output = args.output.resolve()
        output.mkdir(parents=True, exist_ok=False)
    else:
        output = Path(tempfile.mkdtemp(prefix='open-oracle-acceptance-'))
    lines = queue.Queue()
    # No live, decisions, voice, sensor or operator flags are added.
    server = subprocess.Popen([str(python), '-m', 'open_oracle.server',
        '--host', '127.0.0.1', '--port', '0'], cwd=repo,
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True)
    def read_start():
        for line in server.stdout:
            lines.put(line)
            if 'Open Oracle ready at ' in line:
                break
    threading.Thread(target=read_start, daemon=True).start()
    try:
        try:
            line = lines.get(timeout=8)
        except queue.Empty as error:
            raise RuntimeError('Owned exact-source server did not start within eight seconds') from error
        match = re.search(r'http://127\.0\.0\.1:\d+', line)
        if not match:
            raise RuntimeError('Owned server did not announce its loopback URL')
        proof = check_http(match[0])
        (output / 'http-health.json').write_text(json.dumps(proof, indent=2) + '\n')
        subprocess.run(['node', str(browser_script), match[0], str(output)],
                       check=True, timeout=90)
        print(json.dumps({'passed': True, 'owned_server': True,
            'mode': 'exact_source', 'evidence_directory': str(output),
            'physical_capture': False, 'provider_requests': 0,
            'physical_pi': False}, indent=2))
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=2)
        server.stdout.close()
        server.stderr.close()


if __name__ == '__main__':
    try:
        main()
    except (Exception, KeyboardInterrupt) as error:
        print(f'Acceptance stopped: {error}', file=sys.stderr)
        sys.exit(1)
