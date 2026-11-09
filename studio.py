#!/usr/bin/env python3
"""Portable Resume Studio operations: setup, start, stop, package and deploy."""
import argparse
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import time
import urllib.request
import webbrowser
import zipfile

ROOT = Path(__file__).resolve().parent
STATE = ROOT / '.studio'
RECORD = STATE / 'instance.json'
FILES = ['index.html', 'server.py', 'release.py', 'studio.py', 'README.md',
          'resume-builder', 'resume-builder.cmd', 'install_cli.py', 'GUIDE.md', 'SETUP.md',
          'LICENSE', 'CONTRIBUTING.md', 'SECURITY.md', 'PRIVACY.md', 'CHANGELOG.md',
          '.gitattributes', 'docs/ARCHITECTURE.md', 'docs/PUBLISHING.md',
          'docs/images/dashboard.png', 'examples/sample-resume.json',
          '.github/workflows/ci.yml', '.github/workflows/pages.yml',
          '.github/ISSUE_TEMPLATE/bug_report.yml', '.github/ISSUE_TEMPLATE/feature_request.yml',
          '.github/pull_request_template.md',
         'DEPLOYMENT.md', 'Dockerfile', 'Caddyfile', 'compose.yaml', '.dockerignore',
         'Start Resume Studio.command', 'Start Resume Studio.bat', 'test_studio.py',
         'test_operations.py', 'requirements-dev.txt', 'render.yaml', '.gitignore']


def call(command):
    print('+ ' + ' '.join(map(str, command)), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def tool(name):
    path = shutil.which(name)
    if not path:
        raise RuntimeError(f'{name} is not installed or not on PATH. Install it first, then retry.')
    return path


def health(port):
    with urllib.request.urlopen(f'http://127.0.0.1:{port}/api/health', timeout=12) as response:
        return json.load(response)


def record():
    try:
        return json.loads(RECORD.read_text())
    except (OSError, ValueError):
        return None


def running(info):
    try:
        return bool(info and health(info['port']).get('instance') == info['instance'])
    except Exception:
        return False


def start(args):
    previous = record()
    if running(previous):
        url = f'http://127.0.0.1:{previous["port"]}'
        print('Already running: ' + url)
        if not args.no_open:
            webbrowser.open(url)
        return
    STATE.mkdir(exist_ok=True)
    info = {'port': args.port, 'instance': secrets.token_hex(16),
            'admin': secrets.token_urlsafe(32), 'hosted': args.hosted}
    command = [sys.executable, str(ROOT/'server.py'), '--no-open', '--port', str(args.port)]
    if args.hosted:
        command += ['--hosted', '--host', args.host]
    elif args.host != '127.0.0.1':
        raise RuntimeError('External binding requires --hosted; local AI stays on loopback.')
    env = dict(os.environ, STUDIO_ADMIN_TOKEN=info['admin'], STUDIO_INSTANCE=info['instance'])
    log_path = STATE/'server.log'
    flags = {'start_new_session': True} if os.name != 'nt' else {
        'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS}
    with log_path.open('ab') as log:
        process = subprocess.Popen(command, cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                                   stdout=log, stderr=log, **flags)
    info['pid'] = process.pid
    for _ in range(60):
        if process.poll() is not None:
            raise RuntimeError(f'Could not start. Inspect {log_path} (port may be in use).')
        if running(info):
            RECORD.write_text(json.dumps(info), encoding='utf-8')
            if os.name != 'nt':
                RECORD.chmod(0o600)
            url = f'http://127.0.0.1:{args.port}'
            print('Started: ' + url)
            print('Stop with: resume-builder stop (or python3 studio.py stop)')
            if not args.no_open:
                webbrowser.open(url)
            return
        time.sleep(1)
    process.terminate()
    raise RuntimeError(f'Startup timed out. Inspect {log_path}')


def stop():
    info = record()
    if not running(info):
        print('No CLI-managed server running. A manually started launcher must be stopped in its terminal.')
        return
    request = urllib.request.Request(f'http://127.0.0.1:{info["port"]}/api/shutdown',
                                    data=b'{}', headers={'X-Studio-Admin': info['admin']}, method='POST')
    with urllib.request.urlopen(request, timeout=15):
        pass
    for _ in range(20):
        if not running(info):
            RECORD.unlink(missing_ok=True)
            print('Stopped.')
            return
        time.sleep(.25)
    raise RuntimeError('Shutdown is still in progress. Try status again in a few seconds.')


def setup(args):
    if sys.version_info < (3, 9):
        raise RuntimeError('Python 3.9 or newer is required.')
    print('Runtime ready: Python standard library only; nothing to install.')
    if args.dev:
        venv = ROOT/'.venv'
        call([sys.executable, '-m', 'venv', str(venv)])
        python = venv/('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
        call([str(python), '-m', 'pip', 'install', '-r', str(ROOT/'requirements-dev.txt')])
        print('Development dependencies installed. Browser tests use an installed Google Chrome.')


def package(args):
    from release import public_html
    output = Path(args.out).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name in FILES:
            path = ROOT/name
            if not path.exists():
                raise RuntimeError('Missing release file: ' + name)
            data = public_html(hosted=False).encode() if name == 'index.html' else path.read_bytes()
            item = zipfile.ZipInfo('resume-studio/'+name)
            item.external_attr = (0o755 if name.endswith('.command') or name == 'resume-builder' else 0o644) << 16
            archive.writestr(item, data, compress_type=zipfile.ZIP_DEFLATED)
    print(f'Portable bundle: {output}\nContains a blank resume. Export your personal draft as JSON separately.')


def container(args):
    docker = tool('docker')
    prefix = [docker, 'compose', '-p', 'resume-studio', '-f', str(ROOT/'compose.yaml')]
    action = args.action
    call(prefix + ({'up': ['up', '-d', '--build'], 'down': ['down'],
                    'logs': ['logs', '--tail', '100'], 'status': ['ps']}[action]))
    if action == 'up':
        print('Public-mode container: http://localhost:8080 (no personal seed or OpenCode credentials).')


def manifest(image, namespace):
    labels = {'app': 'resume-studio'}
    return {'apiVersion': 'v1', 'kind': 'List', 'items': [
        {'apiVersion': 'apps/v1', 'kind': 'Deployment',
         'metadata': {'name': 'resume-studio', 'namespace': namespace, 'labels': labels},
         'spec': {'replicas': 2, 'selector': {'matchLabels': labels}, 'template': {
             'metadata': {'labels': labels}, 'spec': {'securityContext': {'runAsNonRoot': True, 'runAsUser': 10001, 'fsGroup': 10001},
             'containers': [{'name': 'web', 'image': image, 'ports': [{'containerPort': 8080}],
                             'securityContext': {'allowPrivilegeEscalation': False, 'capabilities': {'drop': ['ALL']}},
                             'resources': {'requests': {'cpu': '50m', 'memory': '32Mi'}, 'limits': {'cpu': '500m', 'memory': '128Mi'}},
                             'readinessProbe': {'httpGet': {'path': '/healthz', 'port': 8080}},
                             'livenessProbe': {'httpGet': {'path': '/healthz', 'port': 8080}, 'initialDelaySeconds': 10}}]}}}},
        {'apiVersion': 'v1', 'kind': 'Service', 'metadata': {'name': 'resume-studio', 'namespace': namespace, 'labels': labels},
         'spec': {'selector': labels, 'ports': [{'port': 80, 'targetPort': 8080}], 'type': 'ClusterIP'}}]}


def pods(args):
    deployment = manifest(args.image, args.namespace)
    if args.action == 'manifest':
        print(json.dumps(deployment, indent=2))
        return
    if not args.context:
        raise RuntimeError('Pass --context explicitly to select the Kubernetes cluster.')
    kubectl = tool('kubectl')
    prefix = [kubectl, '--context', args.context, '--namespace', args.namespace]
    if args.action == 'up':
        subprocess.run(prefix+['apply', '-f', '-'], input=json.dumps(deployment), text=True, check=True)
        call(prefix+['rollout', 'status', 'deployment/resume-studio', '--timeout=120s'])
    elif args.action == 'status':
        call(prefix+['get', 'deployment,pods,service', '-l', 'app=resume-studio'])
    elif args.action == 'down':
        call(prefix+['delete', 'deployment/resume-studio', 'service/resume-studio', '--ignore-not-found'])


def main():
    parser = argparse.ArgumentParser(prog='resume-builder', description=__doc__,
                                     epilog='First time? Run resume-builder guide for the stack, features and usage.')
    parser.add_argument('--version', action='version', version='Resume Studio 1.0.0')
    commands = parser.add_subparsers(dest='command', required=True)
    config = commands.add_parser('setup', help='Check runtime; optionally install test dependencies')
    config.add_argument('--dev', action='store_true')
    for name in ('start', 'restart'):
        sub = commands.add_parser(name, help='Start the app as a managed background process')
        sub.add_argument('--port', type=int, default=8765)
        sub.add_argument('--host', default='127.0.0.1')
        sub.add_argument('--hosted', action='store_true')
        sub.add_argument('--no-open', action='store_true')
    commands.add_parser('setup_guide', help='First-time setup instructions and prerequisites (read-only)')
    for name in ('stop', 'status', 'logs', 'doctor', 'guide'):
        commands.add_parser(name)
    sub = commands.add_parser('build', help='Build a blank public static site for online hosting')
    sub.add_argument('--out', default=str(ROOT/'dist'))
    sub = commands.add_parser('package', help='Create a portable, personal-data-free ZIP')
    sub.add_argument('--out', default=str(ROOT/'resume-studio.zip'))
    sub = commands.add_parser('container', help='Build and operate Docker Compose deployment')
    sub.add_argument('action', choices=['up', 'down', 'status', 'logs'])
    sub = commands.add_parser('pods', help='Generate/apply a Kubernetes Deployment and Service')
    sub.add_argument('action', choices=['manifest', 'up', 'down', 'status'])
    sub.add_argument('--image', required=True, help='Your pushed image, e.g. registry.example.com/resume-studio:1')
    sub.add_argument('--namespace', default='default')
    sub.add_argument('--context')
    args = parser.parse_args()
    try:
        if args.command == 'setup_guide':
            print((ROOT/'SETUP.md').read_text(encoding='utf-8'))
        elif args.command == 'guide':
            print((ROOT/'GUIDE.md').read_text(encoding='utf-8'))
        elif args.command == 'setup':
            setup(args)
        elif args.command in ('start', 'restart'):
            if args.command == 'restart':
                stop()
            start(args)
        elif args.command == 'stop':
            stop()
        elif args.command == 'status':
            info = record()
            print(f'Running on http://127.0.0.1:{info["port"]}' if running(info) else 'Not running under this CLI.')
        elif args.command == 'logs':
            path = STATE/'server.log'
            print(path.read_text(encoding='utf-8', errors='replace')[-12000:] if path.exists() else 'No logs yet.')
        elif args.command == 'doctor':
            from server import find_cli
            print('Python:', sys.version.split()[0])
            print('OpenCode:', find_cli() or 'not found (optional for editor)')
            print('Docker:', shutil.which('docker') or 'not found (optional)')
            print('kubectl:', shutil.which('kubectl') or 'not found (optional)')
        elif args.command == 'build':
            from release import build
            print('Public static site:', build(args.out))
        elif args.command == 'package':
            package(args)
        elif args.command == 'container':
            container(args)
        elif args.command == 'pods':
            pods(args)
    except (RuntimeError, OSError, subprocess.SubprocessError) as error:
        print('Error: ' + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
