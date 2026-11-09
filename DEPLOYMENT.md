# Run anywhere

After the one-time installation in [GUIDE.md](GUIDE.md), replace `python3 studio.py`
in every command below with **`resume-builder`**. For example:
`resume-builder start`, `resume-builder container up`, `resume-builder build`.

All commands below run from the `resume-builder` folder. Use `py -3` instead of
`python3` on Windows. The app runtime needs only Python 3.9+; no pip packages are needed.

## Personal laptop: one command

```sh
python3 studio.py start
```

Starts the local server in the background and opens your browser. OpenCode uses
your installed CLI and provider login. The launcher can now close without stopping
the server. Double-click launchers call this same command.

```sh
python3 studio.py setup             # Verify runtime (nothing to install)
python3 studio.py doctor            # Check Python, OpenCode, Docker, kubectl
python3 studio.py status
python3 studio.py logs
python3 studio.py stop
python3 studio.py restart
python3 studio.py start --port 8766 --no-open
python3 studio.py setup --dev       # Optional isolated test environment + deps
```

The CLI manages only its own instance, using `.studio/instance.json` and a private
shutdown token rather than killing an arbitrary PID. If an old manually launched
server occupies port 8765, stop it in its terminal or select another port.

## Online hosting: recommended static deployment

```sh
python3 studio.py build
```

Upload the resulting **dist/** folder to Cloudflare Pages, Netlify, GitHub Pages,
or another static web host. The site works without Python on the hosting server.
For Render, a `render.yaml` static-site blueprint is included; connect a repository
containing the portable release and select the blueprint deployment workflow.

The build replaces the private sample resume with a blank seed. Publish `dist/`,
**not the original source folder**. No API credentials, review history, or saved
browser drafts are embedded in the build. Deploy behind HTTPS supplied by your host.
Hosting credentials, a repository, and/or a domain must be configured in that service;
this project does not create an account or pay for hosting on your behalf.

### Public mode behavior

- Each visitor's drafts and versions stay in their own browser local storage.
- No shared resume database or user-account system is present.
- Local OpenCode access is absent from public builds and containers. Visitors can
  use the downloaded local app for OpenCode, use their own direct provider API key
  where browser cross-origin access is supported, or export a prompt for any AI.
- Public hosting does not expose your personal OpenCode subscription to visitors.
- API keys entered in direct mode live only in that tab and are sent directly to
  the chosen provider. Resume data leaves the browser only on explicit AI requests
  or exports; saved browser data is not synchronized to the host.

## Docker: one command

Install and start Docker Desktop (Mac/Windows) or Docker Engine + Compose (Linux):

```sh
python3 studio.py container up
# http://localhost:8080
python3 studio.py container status
python3 studio.py container logs
python3 studio.py container down
```

The multi-stage image builds the blank public artifact and serves it with Caddy as
a non-root user. It includes no Python AI backend, OpenCode executable or credentials.
Compose binds to localhost by default. To expose it on a server, set
`STUDIO_BIND=0.0.0.0` and optionally `STUDIO_PORT=8080`, then run `container up`.
Use your platform's HTTPS ingress/reverse proxy and point the domain to that service.
The container itself listens on HTTP port 8080 and exposes `/healthz`.

For a quick LAN preview without Docker (not the recommended public web server):

```sh
python3 studio.py start --hosted --host 0.0.0.0 --port 8080
```

This explicitly disables local AI endpoints and serves a blank starting resume.
The built-in Python server is for local/development use; use static hosting or the
Caddy container for public deployment.

## Kubernetes pods

Build an image, push it to a registry your cluster can pull from, then select an
existing namespace and cluster context explicitly. For mixed CPU architectures,
publish a multi-platform image with Docker buildx or build for your cluster's CPU.

```sh
docker build -t YOUR_REGISTRY/resume-studio:1 .
docker push YOUR_REGISTRY/resume-studio:1
python3 studio.py pods manifest --image YOUR_REGISTRY/resume-studio:1
python3 studio.py pods up --image YOUR_REGISTRY/resume-studio:1 --context YOUR_CONTEXT --namespace default
python3 studio.py pods status --image YOUR_REGISTRY/resume-studio:1 --context YOUR_CONTEXT
python3 studio.py pods down --image YOUR_REGISTRY/resume-studio:1 --context YOUR_CONTEXT
```

`pods up` creates a two-replica Deployment and ClusterIP Service, with readiness and
liveness probes and resource requests/limits, then waits for rollout. It does not
create a public LoadBalancer, DNS record, TLS certificate or registry credential.
Use an existing ingress controller for public access, or preview with:

```sh
kubectl --context YOUR_CONTEXT port-forward service/resume-studio 8080:80
```

## Portable distribution

```sh
python3 studio.py package --out resume-studio.zip
```

The ZIP contains a blank-start copy of the app, portable launchers, CLI, deployment
files and docs. It excludes `.studio`, virtual environments, logs, screenshots,
personal sample data and browser drafts. Export your current resume/versions from
the UI as JSON and transfer that backup separately. Import it on the new machine.

## Features

- Collapsible editor sections; clean unnumbered navigation.
- In-session undo/redo (last 60 changes) and focus-preview mode.
- Named resume versions (up to 30), versions backup/import, word count.
- Eight single-column templates, native PDF export, Markdown/JSON export.
- Local heuristic checks and optional AI feedback. No ATS-pass guarantee.

## Validation status

Local CLI, hosted-mode boundaries, public artifact sanitization, packaging and
browser workflows have automated checks. Docker and Kubernetes commands require
those tools and an accessible engine/cluster; consult the delivery summary for
which environment checks actually ran. Windows launchers are provided, but native
Windows execution must be verified on a Windows machine.
