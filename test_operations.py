"""CLI/release/hosted-mode smoke tests, Python standard library only."""
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import urllib.request
import urllib.error
import zipfile

from release import public_html, BLANK

ROOT = Path(__file__).resolve().parent
PORT = 18766


class OperationsTests(unittest.TestCase):
    def test_setup_guide_without_python(self):
        if os.name == 'nt':
            self.skipTest('POSIX bootstrap test')
        with tempfile.TemporaryDirectory() as tmp:
            # Only the basic shell utilities are available, deliberately no python3.
            import shutil
            for name in ('dirname', 'cat'):
                os.symlink(shutil.which(name), Path(tmp)/name)
            env = dict(os.environ, PATH=tmp)
            guide = subprocess.check_output(['/bin/sh', str(ROOT/'resume-builder'), 'setup_guide'],
                                            env=env, cwd=tmp, text=True)
            self.assertIn('first-time setup', guide)
            self.assertIn('NO third-party runtime Python dependencies', guide)
            failed = subprocess.run(['/bin/sh', str(ROOT/'resume-builder'), 'start'],
                                    env=env, capture_output=True, text=True)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn('setup_guide', failed.stderr)

    def test_command_installer(self):
        with tempfile.TemporaryDirectory(prefix='studio launcher ') as tmp:
            install = [sys.executable, str(ROOT/'install_cli.py'), '--bin-dir', tmp]
            subprocess.run(install, check=True, capture_output=True)
            entry = Path(tmp)/('resume-builder.cmd' if sys.platform == 'win32' else 'resume-builder')
            prefix = [os.environ.get('COMSPEC', 'cmd.exe'), '/d', '/c', str(entry)] if os.name == 'nt' else [str(entry)]
            version = subprocess.check_output(prefix + ['--version'], cwd=tmp, text=True, encoding='utf-8', env=dict(os.environ, PYTHONIOENCODING='utf-8'))
            self.assertIn('Resume Studio', version)
            help_text = subprocess.check_output(prefix + ['start', '--help'], cwd=tmp, text=True, encoding='utf-8', env=dict(os.environ, PYTHONIOENCODING='utf-8'))
            self.assertIn('resume-builder start', help_text)
            guide = subprocess.check_output(prefix + ['setup_guide'], cwd=tmp, text=True, encoding='utf-8', env=dict(os.environ, PYTHONIOENCODING='utf-8'))
            self.assertIn('first-time setup', guide)
            subprocess.run(install+['--uninstall'], check=True, capture_output=True)
            self.assertFalse(entry.exists())
            entry.write_text('Unrelated user command', encoding='utf-8')
            rejected = subprocess.run(install, capture_output=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertEqual(entry.read_text(), 'Unrelated user command')

    def cli(self, *args):
        return subprocess.check_output([sys.executable, str(ROOT/'studio.py'), *args], cwd=ROOT, text=True, encoding='utf-8', env=dict(os.environ, PYTHONIOENCODING='utf-8'), timeout=90)

    def assert_blank_seed(self, html):
        seed = re.search(r'const SEED=(\{.*?\n\});', html, re.S)
        self.assertIsNotNone(seed)
        self.assertEqual(json.loads(seed.group(1)), BLANK)

    def test_public_artifact(self):
        html = public_html()
        self.assert_blank_seed(html)
        self.assertIn('content="hosted"', html)

    def test_build_and_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.cli('build', '--out', str(Path(tmp)/'dist'))
            self.assertIn('content="hosted"', (Path(tmp)/'dist/index.html').read_text())
            bundle = Path(tmp)/'app.zip'
            self.cli('package', '--out', str(bundle))
            with zipfile.ZipFile(bundle) as archive:
                names=archive.namelist()
                self.assertIn('resume-studio/studio.py', names)
                self.assertFalse(any('.studio/' in name or '.venv/' in name for name in names))
                html=archive.read('resume-studio/index.html').decode()
                self.assert_blank_seed(html)
                self.assertIn('content="local"', html)
            manifest=json.loads(self.cli('pods','manifest','--image','example.com/resume-studio:1'))
            self.assertEqual(len(manifest['items']),2)
            self.assertEqual(manifest['items'][0]['spec']['replicas'],2)

    def test_hosted_lifecycle(self):
        # Do not stop or replace a user's managed instance during tests.
        if (ROOT/'.studio/instance.json').exists():
            self.skipTest('A managed instance record exists; stop it before this test.')
        try:
            self.assertIn('Started:', self.cli('start','--hosted','--port',str(PORT),'--no-open'))
            self.assertIn('Already running:', self.cli('start','--hosted','--port',str(PORT),'--no-open'))
            self.assertIn('Running on', self.cli('status'))
            base=f'http://127.0.0.1:{PORT}'
            with urllib.request.urlopen(base+'/api/health') as response:
                health=json.load(response)
                self.assertFalse(health['available'])
                self.assertNotIn('token', health)
            with urllib.request.urlopen(base) as response:
                html=response.read().decode()
                self.assert_blank_seed(html)
            for path,data in [('/api/models',None),('/api/review',b'{}')]:
                with self.assertRaises(urllib.error.HTTPError) as ctx:
                    urllib.request.urlopen(urllib.request.Request(base+path,data=data))
                self.assertIn(ctx.exception.code,(403,404))
            self.assertIn('Stopped.',self.cli('stop'))
            self.assertIn('Not running',self.cli('status'))
        finally:
            self.cli('stop')


if __name__ == '__main__':
    unittest.main()
