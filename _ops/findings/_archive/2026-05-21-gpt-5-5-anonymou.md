# Findings — 2026-05-21 — gpt-5-5 — sess:anonymou

- 14:55 — global 1* Codex skills audit: 4/22 fail qv-skill | 1findings + 1planning angle brackets; 1instruction-layer + retired docs-skill description >1024 | source: current /Users/triton/.codex/skills audit
- 16:39 — md-mcp current Codex session exposes stale 0.3.0 registry while repo smoke for configured server passes 0.4.0 with 19 tools | /Users/triton/.codex/config.toml + npm run smoke | future agents may need session restart before MCP-only workflows are reliable
- 22:47 — _ops/AGENTS.md still routes hot findings through problems/ while root AGENTS.md, roadmap, 1start-here, and 1findings use _ops/findings/ | _ops/AGENTS.md:24,68 vs AGENTS.md:66,127 and ~/.codex/skills/1findings/SKILL.md:42,69 | future agent may write to nonexistent/stale layer
