# Resume Builder — first-time setup

Just cloned or extracted the project? Start here. This guide only prints
instructions; it does not install software or change your machine.

## 1. Open a terminal in the project folder

Mac / Linux:

    ./resume-builder setup_guide

If the executable permission was lost while copying:

    chmod +x resume-builder
    ./resume-builder setup_guide

Windows PowerShell:

    .\resume-builder.cmd setup_guide

Windows Command Prompt:

    resume-builder.cmd setup_guide

These folder-local setup-guide commands work without Python installed.

## 2. Choose how you want to run the app

EDITOR ONLY: open index.html in Chrome, Edge, Firefox or Safari. No Python,
Node, pip packages or internet connection is required for editing and PDF export.
Local OpenCode integration needs the server mode below.

FULL LOCAL APP: install Python 3.9 or newer and use a modern browser.
There are NO third-party runtime Python dependencies. No npm install,
pip install, virtual environment or database setup is required to start it.

## 3. Install or check Python (full local app)

Mac / Linux:

    python3 --version

If Python is absent or older than 3.9:
- macOS: install from https://www.python.org/downloads/macos/
  Or, if you already use Homebrew: brew install python
- Linux: install Python 3.9+ using your distribution's package manager.

Windows:

    py -3 --version

Install from https://www.python.org/downloads/windows/ if needed. Enable
the Python launcher and the option to add Python to PATH, then reopen the terminal.
If the launcher is unavailable but Python is on PATH, use python instead of py -3.

## 4. Start directly from the folder

Mac / Linux:

    ./resume-builder setup
    ./resume-builder doctor
    ./resume-builder start

Windows PowerShell:

    .\resume-builder.cmd setup
    .\resume-builder.cmd doctor
    .\resume-builder.cmd start

setup checks the runtime; it has no runtime packages to install.
doctor reports optional tools; their absence does not prevent editing.
start opens http://127.0.0.1:8765 and keeps the server running in the background.
Use the same entry point with stop to shut it down.

## 5. Optional: install the short command for use from any directory

Mac / Linux:

    python3 install_cli.py

Follow the PATH instructions printed by the installer. Add the provided export
line to your shell profile (~/.zshrc on most Macs), then open a new terminal.
Alternatively, choose an existing writable directory on PATH with --bin-dir.

Windows:

    py -3 install_cli.py --add-path

Open a new terminal. You can now run from any directory:

    resume-builder setup_guide
    resume-builder start
    resume-builder status
    resume-builder stop
    resume-builder --help

The installed launcher points to this project folder and your Python executable.
If you move the folder or change Python, rerun the installer from the new location.

## 6. Optional tools — install only for features you need

OpenCode AI reviews:
- Install OpenCode using https://opencode.ai/docs/ and sign in to a provider.
- Check: opencode --version
- Check: opencode models
- Start the app using the local launcher, then use AI review -> OpenCode.
- Your chosen model provider receives the resume/job text; usage limits apply.

Docker containers:
- Install/start Docker Desktop (Mac/Windows) or Docker Engine + Compose (Linux).
- Check: docker info
- Run: resume-builder container up

Kubernetes pods:
- Install kubectl and configure credentials for your cluster and image registry.
- Read DEPLOYMENT.md before using resume-builder pods up.

Development/testing only:
- Run: resume-builder setup --dev
- This creates .venv and installs Playwright/pypdf for automated tests.
- Browser tests also require Google Chrome.

## 7. Save your work and move it between computers

Drafts and named versions are saved in your browser, not in the project folder.
Export JSON from the app before changing browser, laptop, URL or port. Import
that backup on the new machine. Use Versions to back up all saved versions.

## 8. Hosting and packaging

    resume-builder build       Generate a blank public site in dist/
    resume-builder package     Generate the portable resume-studio.zip

Deploy dist/ to an HTTPS static host. Do not publish the private source folder
as your website. Public builds omit personal sample data and local OpenCode
access. See DEPLOYMENT.md for containers, Render and Kubernetes instructions.

## Troubleshooting

- Permission denied: chmod +x resume-builder, or run sh ./resume-builder setup_guide.
- Command not found: use the folder-local entry point first; then follow step 5.
- Port already in use: resume-builder start --port 8766.
- OpenCode not found: editing still works; install it only if you want local AI.
- Docker unavailable: start the Docker engine before container up.
- Startup failure: resume-builder logs and resume-builder doctor.

Next: resume-builder guide explains the architecture and features.
