#!/usr/bin/env python3
"""Install a small resume-builder launcher without pip or administrator access."""
import argparse
import os
from pathlib import Path
import shlex
import sys

ROOT = Path(__file__).resolve().parent
MARKER = 'Resume Studio managed launcher'


def windows_path(directory):
    import winreg
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, 'Environment') as key:
        try:
            old, _ = winreg.QueryValueEx(key, 'Path')
        except FileNotFoundError:
            old = ''
        normalized = str(directory).rstrip('\\').lower()
        if normalized not in [os.path.expandvars(p).rstrip('\\').lower() for p in old.split(';')]:
            winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ,
                             old.rstrip(';') + (';' if old else '') + str(directory))
    # Notify Explorer so newly opened terminals inherit the user PATH.
    import ctypes
    result = ctypes.c_size_t()
    ctypes.windll.user32.SendMessageTimeoutW(0xffff, 0x001A, 0, 'Environment',
                                           2, 5000, ctypes.byref(result))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    default = (Path(os.environ.get('LOCALAPPDATA', str(Path.home()/'AppData/Local')))/'ResumeStudio/bin'
               if os.name == 'nt' else Path.home()/'.local/bin')
    parser.add_argument('--bin-dir', type=Path, default=default,
                        help='Directory for the command launcher (choose a directory on PATH)')
    parser.add_argument('--add-path', action='store_true', help='Windows only: add the directory to user PATH')
    parser.add_argument('--uninstall', action='store_true', help='Remove this managed command launcher')
    args = parser.parse_args()
    directory = args.bin_dir.expanduser().resolve()
    target = directory / ('resume-builder.cmd' if os.name == 'nt' else 'resume-builder')
    if args.add_path and os.name != 'nt':
        parser.error('--add-path is Windows-only; add the printed export line to your shell profile instead.')
    try:
        if target.exists() or target.is_symlink():
            if target.is_symlink() or MARKER not in target.read_text(encoding='utf-8'):
                parser.error(f'Refusing to overwrite an unrelated command: {target}')
        if args.uninstall:
            target.unlink(missing_ok=True)
            print(f'Removed launcher: {target}\nYour app folder, drafts and PATH settings were not changed.')
            return 0
        directory.mkdir(parents=True, exist_ok=True)
        python = str(Path(sys.executable).resolve())
        entry = str(ROOT/'studio.py')
        if os.name == 'nt':
            # Escape percent expansion in batch-file paths.
            text = f'@echo off\nrem {MARKER}\n"{python.replace(chr(37), chr(37)*2)}" "{entry.replace(chr(37), chr(37)*2)}" %*\n'
        else:
            text = f'#!/bin/sh\n# {MARKER}\nexec {shlex.quote(python)} {shlex.quote(entry)} "$@"\n'
        target.write_text(text, encoding='utf-8')
        if os.name != 'nt':
            target.chmod(0o755)
        if args.add_path:
            windows_path(directory)
        print(f'Installed: {target}\nApp folder: {ROOT}')
        print('Try: resume-builder --help')
        if os.name == 'nt' and args.add_path:
            print('Open a new terminal to use the updated PATH.')
        elif str(directory) not in os.environ.get('PATH', '').split(os.pathsep):
            if os.name == 'nt':
                print('Rerun with --add-path, then open a new terminal.')
            else:
                print('Add this line to ~/.zshrc (Mac) or your shell profile, then open a new terminal:')
                print(f'export PATH={shlex.quote(str(directory))}:"$PATH"')
        print('If you move the app folder or change Python, rerun this installer from the new location.')
        return 0
    except OSError as error:
        print(f'Installation failed: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
