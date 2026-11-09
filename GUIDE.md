# Resume Builder — quick guide

First time after cloning? Run `./resume-builder setup_guide` (Mac/Linux) or
`.\resume-builder.cmd setup_guide` (Windows PowerShell). This works before Python
is installed. The installed command also supports `resume-builder setup_guide`.

## Install the command once

Mac/Linux, from the app folder:

    python3 install_cli.py

The installer prints a PATH line if needed. Add that line to your shell profile
(~/.zshrc on most Macs), then open a new terminal. If you already have a writable
directory on PATH, choose it with --bin-dir, for example:

    python3 install_cli.py --bin-dir /opt/homebrew/bin

Windows, from the app folder:

    py -3 install_cli.py --add-path

Open a new terminal. Now `resume-builder` works from any directory. The launcher
points to this app folder and the Python used during installation; moving either
requires rerunning the installer. No pip package or administrator privileges needed.

Without installing, use `./resume-builder start` on Mac/Linux (make it executable
with `chmod +x resume-builder` if necessary) or `resume-builder.cmd start` in Windows
Command Prompt (`.\resume-builder.cmd start` in PowerShell).

## Everyday commands

    resume-builder start                 Start in background and open browser
    resume-builder status                Check the CLI-managed server
    resume-builder stop                  Stop that server
    resume-builder restart               Restart the server
    resume-builder logs                  Show recent server output
    resume-builder doctor                Check Python/OpenCode/Docker/kubectl
    resume-builder setup                 Check runtime; no dependencies to install
    resume-builder setup_guide           Read first-time installation instructions
    resume-builder setup --dev           Install optional tests into .venv
    resume-builder --help                Show commands
    resume-builder start --help          Show options for one command
    resume-builder guide                 Read this guide in your terminal
    resume-builder --version             Show the app version

The default address is http://127.0.0.1:8765. Use `start --port 8766` for a different
port. `start --no-open` avoids opening the browser. The commands operate on the app
folder's managed instance, regardless of your current working directory.

## What we built it with

| Layer | Technology | Purpose |
|---|---|---|
| Dashboard | HTML, CSS, vanilla JavaScript | Forms, templates, preview and interactions; no Node/build step |
| Draft storage | Browser localStorage | Current draft, preferences and named versions |
| Local launcher/API | Python 3.9+ standard library | Start/stop, local HTTP API, OpenCode process integration |
| AI integration | Installed OpenCode CLI | Reuses your configured models and provider login |
| Optional AI | Anthropic/OpenAI browser API calls | Bring-your-own-key review, subject to provider CORS support |
| PDF export | Browser native printing | Selectable-text PDF, with A4 layout controls |
| Public build | Python release builder | Generates a blank static site with private sample data removed |
| Container hosting | Multi-stage Docker + Caddy | Non-root static HTTP service, no OpenCode credentials |
| Cluster deployment | Kubernetes Deployment + Service | Two replicas, health probes and resource limits |
| Tests | Playwright, pypdf, unittest | Browser behavior, PDF text and CLI/release checks |

There is no SQL database, login/account system, cloud draft synchronization or
shared AI-credit pool. The local Python HTTP server is for personal/development
use; static hosting or the Caddy container is the public deployment path.

## Features you can use

- Content: contact, summary, skills, experience bullets, projects, education and
  certifications. Reorder entries; use **bold** to emphasize bullet lead phrases.
- Templates: ATS Classic, Compact, Serif Modern, Impact, Engineering, Executive,
  Minimal and Academic. Adjust typography/margins or Auto-fit to one page.
- Editing: collapsible sections, word count, focus preview and 60-change undo/redo.
- Versions: save up to 30 named application-specific versions; restore or delete
  them and export/import a versions backup.
- Checks: local writing/formatting checks and approximate job-description keyword
  overlap. The score is a heuristic, not an employer ATS score or hiring guarantee.
- AI review: model selection, analysis, before/after suggestions, cancellation,
  review copy/download. Suggestions are not silently applied to your resume.
- AI prompt export: review with another assistant without connecting an API here.
- Export: PDF, Markdown, current resume JSON and all-versions JSON.
- Portability: blank-start ZIP, Mac/Windows launchers and offline editor use.

## Suggested workflow

1. Run `resume-builder start`.
2. Fill Content or import your existing JSON from Export.
3. Pick a template and check the preview.
4. Paste the target job description in Checks.
5. In AI review, select OpenCode and a configured model, then Analyze resume.
6. Review the suggestions and edit only accurate claims.
7. Save a named version, then export PDF and a JSON backup.

Browser drafts are device-, browser-, and URL-specific. Moving from file:// to the
local server, or changing ports, means a separate storage location. Transfer JSON
backups to move drafts between them. Browser storage clearing can delete drafts.
Undo history is in memory and resets on reload; saved versions persist.

## Sharing and deployment

    resume-builder build                 Generate the public site in dist/
    resume-builder package               Generate resume-studio.zip
    resume-builder container up          Build/start Docker Compose
    resume-builder container status
    resume-builder container logs
    resume-builder container down

Upload dist/ to an HTTPS static host. The generated ZIP excludes your personal
sample resume, drafts, credentials and logs; export personal JSON separately.

For Kubernetes, first build and push an image to your registry, then:

    resume-builder pods manifest --image YOUR_REGISTRY/resume-studio:1
    resume-builder pods up --image YOUR_REGISTRY/resume-studio:1 --context YOUR_CONTEXT

See DEPLOYMENT.md for registry, namespace, ingress, HTTPS and Render instructions.
Docker needs a running engine; Kubernetes needs a configured cluster and credentials.
These commands do not create cloud accounts, domains or registry credentials.

## Local versus public AI

Local mode runs OpenCode on your machine, with tool access denied for the review
process. Your selected model provider receives the resume/job text; subscription
limits apply, and OpenCode may retain the review in local session history.

Public builds have no local OpenCode endpoint. Visitors use their own direct API
key when supported or export a prompt. Their drafts stay in their own browsers.

## Remove the installed command

    python3 install_cli.py --uninstall --bin-dir /opt/homebrew/bin

Use the directory you chose during installation. On Windows:

    py -3 install_cli.py --uninstall

This removes only the managed command launcher, not drafts or the app folder.
