# Security reporting

Please do not put credentials, personal resumes, exploit details or sensitive logs
in public issues. If the repository's **Security → Report a vulnerability** option
is enabled, use it for a private report. Otherwise, open a minimal issue asking the
maintainer to enable private reporting, without publishing vulnerability details.

The project is maintained on a best-effort basis; no response-time SLA is offered.
Include the affected version, reproduction steps using synthetic data, impact and
suggested mitigation in the private report.

## Boundaries

- Local OpenCode endpoints bind to loopback and validate request origin/host and
  a per-launch token for write requests. Do not expose local mode through a tunnel.
- Public builds and containers serve static assets only, without OpenCode access.
- The Python server is not intended as a hardened public application server.
- The app uses inline JavaScript/styles and localStorage; it is not an encrypted
  vault. Anyone with access to your browser profile may access saved drafts.
- Provider calls transmit resume content. Local OpenCode may keep session history.

Read [PRIVACY.md](PRIVACY.md) for data flow and [DEPLOYMENT.md](DEPLOYMENT.md) before
hosting. Publishers should enable GitHub private vulnerability reporting and serve
public builds over HTTPS.
