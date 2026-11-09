# Publish on GitHub

## Choose the clean source

Use the prepared GitHub-ready folder or extract `resume-studio.zip`. The portable
package uses a file allowlist and removes personal sample data. Do not upload the
entire personal working directory: it may contain logs, screenshots and browser
backups outside that allowlist.

The public repository includes MIT licensing, setup/user/deployment docs, fictional
example data, issue/PR templates, CI and a manual Pages workflow. The app starts blank.

## Create and push a repository

Create an empty GitHub repository named `resume-builder` (or your preferred name).
Then, from the clean folder:

```sh
git init -b main
git add .
git status
git diff --cached --stat
git commit -m "Initial Resume Builder release"
git remote add origin https://github.com/YOUR_USERNAME/resume-builder.git
git push -u origin main
```

Replace the placeholder username. Inspect staged files before committing. You can
also use GitHub's web upload, but include `.github` and other dotfiles; ZIP archives
do not become browsable source unless extracted first. If Unix executable modes
were lost while transferring files, use:

```sh
git update-index --chmod=+x resume-builder "Start Resume Studio.command"
```

Suggested repository description: **Local-first resume builder with templates,
OpenCode AI review, PDF export and a portable Python CLI.**

Suggested topics: `resume-builder`, `python`, `opencode`, `local-first`, `pdf`, `docker`.

## Enable a public demo with GitHub Pages

1. Open repository **Settings → Pages**, choose **GitHub Actions** as the source.
2. Open **Actions → Deploy Pages**, click **Run workflow** from your default branch.
3. The workflow builds `dist/` and deploys a blank hosted-mode editor.
4. Use the URL reported by the deployment job; repository names and owners are
   resolved by GitHub, not hardcoded in the source.

Pages availability depends on your repository/account plan. The workflow has no
AI provider credentials and exposes no local OpenCode service. Public visitors
store their own drafts in their browsers. See DEPLOYMENT.md for alternative hosts.

## Repository settings and releases

- Enable private vulnerability reporting in **Settings → Security** if available.
- Let CI finish before merging changes; add branch protection if desired.
- Update CHANGELOG.md for changes and use a release tag, such as `v1.0.0`.
- Attach `resume-studio.zip` to a release for users who prefer a portable download.
- CI is configured for three OSes, but do not claim a green matrix until the jobs
  have actually run in your repository.
