# Contributing

## Get started

1. Fork and clone the repository.
2. Run the folder-local `setup_guide` command described in [SETUP.md](SETUP.md).
3. Create a branch for one focused change.
4. Make the change, add meaningful tests, and update relevant documentation.
5. Open a pull request describing the behavior, checks performed and any limitations.

Runtime code requires Python 3.9+ but no third-party packages. The UI is vanilla
JavaScript inside `index.html`. Keep the offline editor self-contained; avoid new
remote scripts, fonts or runtime dependencies without discussing the tradeoff.

## Tests

```sh
python3 test_operations.py
python3 studio.py setup --dev
```

Activate `.venv` (`source .venv/bin/activate` on Mac/Linux, or
`.\.venv\Scripts\Activate.ps1` in PowerShell). Then:

```sh
python test_studio.py
```

By default this uses an installed Google Chrome and **mocked AI responses/model
discovery**, so it requires no OpenCode login and makes no provider requests.
For a Playwright-managed browser:

```sh
python -m playwright install chromium
python test_studio.py --browser chromium
```

For an explicitly requested live integration test:

```sh
python test_studio.py --live --model provider/model
```

Live tests require your configured OpenCode installation, submit synthetic data,
and may consume provider quota. Never add keys or tokens to tests or CI.

CLI tests use port 18766, browser tests use port 18765. Stop any previous test
server occupying those ports. Managed-instance lifecycle tests skip if an existing
`.studio/instance.json` is present to avoid interfering with your running app.

## UI changes

Check keyboard navigation, narrow layouts, focus preservation, JSON round-trips,
and print output. PDF tests extract text, not just count font objects. If screenshots
are needed for documentation, use `examples/sample-resume.json` (fictional data).

## Public releases

`resume-builder package` uses an explicit allowlist, including docs and workflows.
Add new distribution files to `FILES` in `studio.py`. Do not add browser backups,
logs, generated screenshots containing personal data, credentials or runtime state.
Run the public-build and packaging tests before submitting.

## Collaboration

Be respectful, explain tradeoffs, and keep reviews focused on the code. Bug reports
should include clear steps, expected behavior, OS/browser versions and sanitized
logs. Use [SECURITY.md](SECURITY.md) for sensitive reports.
