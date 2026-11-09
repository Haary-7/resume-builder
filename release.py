"""Build a public HTML artifact without the private sample resume."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
BLANK = {
    'template': 't-classic', 'type': {'fs': 10, 'lh': 1.3, 'pad': 12, 'acc': '#1a1a1a'},
    'basics': {'name': '', 'title': '', 'location': '', 'phone': '', 'email': '', 'links': []},
    'summary': '', 'skills': [{'label': 'Skills', 'value': ''}],
    'experience': [{'role': '', 'company': '', 'client': '', 'location': '',
                    'start': '', 'end': 'Present', 'scope': '', 'bullets': ['']}],
    'projects': [], 'education': [{'degree': '', 'school': '', 'year': ''}],
    'certs': [], 'jd': ''
}


def public_html(hosted=True):
    source = (ROOT / 'index.html').read_text(encoding='utf-8')
    source, count = re.subn(r'const SEED=\{.*?\n\};',
                           lambda _: 'const SEED=' + json.dumps(BLANK, indent=2) + ';',
                           source, count=1, flags=re.S)
    if count != 1:
        raise ValueError('Could not isolate sample resume; refusing to publish.')
    source = source.replace('/* ========================= SEED (your real resume) ========================= */',
                            '/* Blank resume for new visitors. */')
    if hosted:
        source = source.replace('name="studio-mode" content="local"',
                                'name="studio-mode" content="hosted"')
    return source


def build(destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / 'index.html').write_text(public_html(), encoding='utf-8')
    (destination / '_headers').write_text(
        '/*\n  X-Content-Type-Options: nosniff\n  X-Frame-Options: DENY\n'
        '  Referrer-Policy: no-referrer\n  Permissions-Policy: camera=(), microphone=(), geolocation=()\n',
        encoding='utf-8')
    return destination


def source_release(destination):
    """Export only allowlisted source; never merge into an existing directory."""
    import shutil
    from studio import FILES
    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError('Choose a new directory; source export never overwrites existing work.')
    missing = [name for name in FILES if not (ROOT/name).is_file()]
    if missing:
        raise ValueError('Missing source files: ' + ', '.join(missing))
    destination.mkdir(parents=True)
    for name in FILES:
        target = destination/name
        target.parent.mkdir(parents=True, exist_ok=True)
        if name == 'index.html':
            target.write_text(public_html(hosted=False), encoding='utf-8')
        else:
            shutil.copyfile(ROOT/name, target)
        if name == 'resume-builder' or name.endswith('.command'):
            target.chmod(0o755)
    return destination


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', default='dist')
    parser.add_argument('--source-out', help='Export a clean GitHub-ready source tree into a new directory')
    args = parser.parse_args()
    print(source_release(args.source_out) if args.source_out else build(args.out))
