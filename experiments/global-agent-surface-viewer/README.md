# Global Agent Surface Viewer

Local read-only viewer for global Codex and Claude agent surfaces.

It uses Docsify for Markdown navigation and a small Node server as a whitelist
gateway to live files under `~/.codex`, `~/.claude`, and `~/.agents`.

## Run

```bash
npm install
npm run check
npm run dev
```

Open:

```text
http://127.0.0.1:8765
```

Optional port:

```bash
node server.js --port 8766
```

## Boundary

The viewer does not copy global file contents into this repo. Every Docsify page
is generated from the current source file on request.

The server only exposes a small allowlist: skills, global instructions, hooks,
agents, and runtime config files. Auth, sessions, logs, state, caches, backups,
databases, build output, and dependency folders are excluded.
