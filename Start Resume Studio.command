#!/bin/zsh
SCRIPT_DIR="${0:A:h}"
if ! command -v python3 >/dev/null 2>&1; then
  printf 'Python 3.9+ is required. Install from https://www.python.org/downloads/\n'
  read '?Press Enter to close.'
  exit 1
fi
python3 "$SCRIPT_DIR/studio.py" start
