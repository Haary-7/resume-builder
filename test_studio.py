"""Integration checks. Requires playwright and pypdf only in the test environment.

Run: python test_studio.py [--live] [--model provider/model]
--live makes one real, synthetic-data OpenCode request.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import urllib.request
import urllib.error

from playwright.sync_api import sync_playwright
from pypdf import PdfReader
from release import public_html

ROOT = Path(__file__).resolve().parent
BASE = 'http://127.0.0.1:18765'


def request(path, data=None, token=None, origin=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['X-Studio-Token'] = token
    if origin:
        headers['Origin'] = origin
    req = urllib.request.Request(BASE + path, data=json.dumps(data).encode() if data is not None else None, headers=headers)
    with urllib.request.urlopen(req, timeout=45) as response:
        return json.load(response)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--model', default='')
    parser.add_argument('--browser', choices=['chrome', 'chromium'], default='chrome')
    parser.add_argument('--docs-screenshot', action='store_true', help='Refresh the README screenshot with fictional data')
    args = parser.parse_args()
    env=os.environ.copy()
    if not args.live:
        env['OPENCODE_BIN']=str(ROOT/'nonexistent-test-opencode')
    server = subprocess.Popen([sys.executable, str(ROOT/'server.py'), '--no-open', '--port', '18765'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,env=env)
    try:
        for _ in range(60):
            try:
                health = request('/api/health')
                break
            except Exception:
                time.sleep(1)
        else:
            raise RuntimeError('Server did not start')
        token = health['token']
        for options in ({'data': {'resume': 'test'}}, {'data': {'resume': 'test'}, 'token': token, 'origin': 'https://example.com'}):
            try:
                request('/api/review', **options)
                raise AssertionError('Cross-origin or tokenless request accepted')
            except urllib.error.HTTPError as error:
                assert error.code == 403
        try:
            request('/api/review', {'resume': 'test', 'model': 'bad;command'}, token)
            raise AssertionError('Unsafe model ID accepted')
        except urllib.error.HTTPError as error:
            assert error.code == (400 if health['available'] else 503)
        print('PASS local request boundaries and input validation')

        with tempfile.TemporaryDirectory(prefix='resume-studio-tests-') as tmp, sync_playwright() as pw:
            browser = pw.chromium.launch(**({'channel':'chrome'} if args.browser=='chrome' else {}), headless=True)
            page = browser.new_page(viewport={'width': 1512, 'height': 1100})
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(BASE)
            fixture=json.loads((ROOT/'examples/sample-resume.json').read_text(encoding='utf-8'))
            page.evaluate('(fixture)=>{S=fixture;redraw()}',fixture)
            if args.docs_screenshot:
                screenshot_dir=ROOT/'docs/images'
                screenshot_dir.mkdir(parents=True,exist_ok=True)
                page.screenshot(path=str(screenshot_dir/'dashboard.png'),full_page=True)
            page.locator('[data-p="basics.name"]').fill('Integration Test Candidate')
            assert page.locator('#page .nm').inner_text() == 'Integration Test Candidate'
            page.reload()
            assert page.locator('[data-p="basics.name"]').input_value() == 'Integration Test Candidate'
            page.locator('[data-tab="design"]').click()
            assert page.locator('.tpl-card').count() == 8
            for card in page.locator('.tpl-card').all():
                card.click()
                template = card.get_attribute('data-t')
                assert template in page.locator('#page').get_attribute('class')
                assert page.locator('#page').evaluate('(p)=>p.offsetWidth') > 790
                pdf_path = Path(tmp)/(template+'.pdf')
                page.pdf(path=str(pdf_path), prefer_css_page_size=True, print_background=True)
                reader = PdfReader(str(pdf_path))
                text = '\n'.join(p.extract_text() for p in reader.pages)
                normalized = ' '.join(text.split())
                assert 'Integration Test Candidate' in normalized and 'education' in normalized.lower(), repr(text[:1000])
                assert 'Make your next move' not in text
                print('PASS template and extractable PDF:', template, len(reader.pages), 'page(s)')
                if len(reader.pages) > 1:
                    page.locator('.advanced-controls').evaluate('(d)=>d.open=true')
                    page.get_by_role('button', name='Auto-fit to one page', exact=True).click()
                    page.pdf(path=str(pdf_path), prefer_css_page_size=True, print_background=True)
                    assert len(PdfReader(str(pdf_path)).pages) == 1, 'Auto-fit failed for '+template
            page.locator('[data-t="t-classic"]').click()
            page.locator('[data-tab="content"]').click()
            name=page.locator('[data-p="basics.name"]')
            name.fill('Undo Candidate')
            page.locator('#undoButton').click()
            assert page.locator('#page .nm').inner_text() == 'Integration Test Candidate'
            page.locator('#redoButton').click()
            assert page.locator('#page .nm').inner_text() == 'Undo Candidate'
            page.locator('[data-tab="library"]').click()
            page.locator('#versionName').fill('Platform role')
            page.get_by_role('button',name='Save version',exact=True).click()
            page.locator('[data-tab="content"]').click()
            page.locator('[data-p="basics.name"]').fill('Changed draft')
            page.locator('[data-tab="library"]').click()
            page.get_by_role('button',name='Load',exact=True).click()
            assert page.locator('#page .nm').inner_text() == 'Undo Candidate'
            with page.expect_download() as downloaded:
                page.get_by_role('button',name='Export all versions',exact=True).click()
            versions_backup=Path(tmp)/'versions.json'
            downloaded.value.save_as(str(versions_backup))
            page.locator('#versionsFile').set_input_files(str(versions_backup))
            page.wait_for_timeout(200)
            assert page.locator('.version-card').count() == 2
            page.locator('#focusButton').click()
            assert not page.locator('.left').is_visible()
            page.locator('#focusButton').click()
            assert page.locator('.left').is_visible()
            assert all(not label[:1].isdigit() for label in page.locator('.tab').all_text_contents())
            page.locator('[data-tab="ats"]').click()
            jd = page.locator('#jdBox')
            jd.fill('Platform engineer with Python Linux CI/CD and monitoring experience. Strong automation and software delivery skills required.')
            jd.focus()
            page.wait_for_timeout(650)
            assert page.evaluate('document.activeElement.id') == 'jdBox'
            page.locator('[data-tab="export"]').click()
            original = page.locator('#page .nm').inner_text()
            page.locator('#loadF').set_input_files({'name': 'bad.json', 'mimeType': 'application/json', 'buffer': b'{"basics": {}}'})
            page.wait_for_timeout(200)
            assert page.locator('#page .nm').inner_text() == original
            with page.expect_download() as downloaded:
                page.get_by_role('button', name='Download .json', exact=True).click()
            exported = Path(tmp)/'resume.json'
            downloaded.value.save_as(str(exported))
            assert json.loads(exported.read_text())['basics']['name'] == original
            page.locator('#loadF').set_input_files(str(exported))
            page.wait_for_timeout(200)
            assert page.locator('#page .nm').inner_text() == original
            if not args.live:
                page.route('**/api/health',lambda route:route.fulfill(json={'available':True,'version':'test-mock','token':'test-token'}))
                page.route('**/api/models',lambda route:route.fulfill(json={'models':['example/model']}))
            page.locator('[data-tab="ai"]').click()
            page.wait_for_function("document.getElementById('ocStatus').textContent.includes('models available')", timeout=45000)
            assert page.locator('#ocModel option').count() > 1
            def fake_review(route):
                if route.request.method == 'POST':
                    route.fulfill(json={'id': 'browser-test'})
                else:
                    route.fulfill(json={'state': 'done', 'text': 'SUMMARY\nSynthetic review completed. Keep the measurable outcomes.'})
            page.route('**/api/review*', fake_review)
            page.locator('#reviewButton').click()
            assert page.locator('#reviewButton').is_disabled()
            page.locator('#aiOut').get_by_text('SUMMARY', exact=False).wait_for(timeout=10000)
            assert not page.locator('#reviewButton').is_disabled()
            page.locator('[data-tab="content"]').click()
            page.locator('[data-tab="ai"]').click()
            assert 'Synthetic review completed' in page.locator('#aiOut').inner_text()
            page.unroute('**/api/review*', fake_review)
            page.set_viewport_size({'width': 390, 'height': 844})
            page.wait_for_timeout(200)
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
            page.screenshot(path=str(ROOT/'studio-mobile.png'), full_page=True)
            page.set_viewport_size({'width': 1512, 'height': 1100})
            page.locator('[data-tab="content"]').click()
            page.screenshot(path=str(ROOT/'studio-preview.png'), full_page=True)
            public_page=browser.new_page()
            public_page.on('pageerror',lambda error: errors.append(str(error)))
            public_page.route('**/public-test',lambda route:route.fulfill(body=public_html(),content_type='text/html'))
            public_page.goto(BASE+'/public-test')
            assert public_page.locator('[data-p="basics.name"]').input_value() == ''
            public_page.locator('[data-p="basics.name"]').fill('Public Visitor')
            public_page.locator('[data-tab="ai"]').click()
            assert public_page.locator('#aiProv option[value="opencode"]').count() == 0
            public_page.locator('[data-tab="content"]').click()
            public_page.reload()
            assert public_page.locator('[data-p="basics.name"]').input_value() == 'Public Visitor'
            public_page.close()
            assert not errors, errors
            print('PASS persistence, versions/backup, undo/redo, focus mode, public blank-state/isolation, JD focus, import/export, OpenCode discovery, AI UI lifecycle, mobile layout and JS console')
            browser.close()

        if args.live:
            started = request('/api/review', {'resume': 'Example Candidate. Platform engineer, 2022–present. Built Python scripts and Jenkins pipelines for 20 Linux hosts. B.Tech 2022.', 'job': 'Platform engineer using Linux and Python.', 'model': args.model}, token)
            for _ in range(210):
                result = request('/api/review?id=' + started['id'])
                if result['state'] != 'running':
                    break
                time.sleep(1)
            assert result['state'] == 'done', result
            assert len(result['text']) > 100
            print('PASS live OpenCode review:', len(result['text']), 'characters')
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()


if __name__ == '__main__':
    main()
