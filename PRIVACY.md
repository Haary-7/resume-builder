# Data and privacy

## Stored in the browser

The current resume, saved versions and preferences are stored in localStorage for
the page's origin. They are not encrypted. Undo/redo history and AI review output
are held in memory. JSON exports contain resume data but no API keys. Review text
can be downloaded separately. Clear the browser's site data to remove local drafts;
export a backup first if you need to keep them.

The application includes no analytics, advertising, CDN dependencies or automatic
resume upload. Public hosting providers may retain normal access logs according
to their own policies.

## AI requests

- **OpenCode:** the local Python bridge supplies resume/job text to your CLI and
  selected model provider. Provider policies and quotas apply. OpenCode may retain
  its own session history, independently of this app.
- **Direct APIs:** requests go from the browser to the selected provider. API keys
  are held in the open tab, not saved in exports or localStorage.
- **Prompt export:** creates a local text download; sending it to another AI is
  your choice.

The bridge keeps its current review result in memory; it does not write resume
files. Operational logs should not contain prompts or tokens. Public mode disables
local AI endpoints and does not provide a shared provider account.

## Portability

Each browser, device and URL/port has separate storage. File-based and localhost
sessions do not share drafts. Copying the app folder does not copy browser data;
use the JSON export/import features. Do not upload personal backups into GitHub.
