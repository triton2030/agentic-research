---
description: "Agent, skills, sandbox and observability routes in Vercel CLI 59.1.4."
---

# Vercel CLI 59: Agent Platform

Момент: до ручного API/helper-а выбирается Vercel agent/platform route. Сверено
2026-08-19 с active Vercel CLI 59.1.4; beta/preview families меняются быстро.

## Дельта

| Старый вероятный путь | Active route |
|---|---|
| вручную собирать Vercel guidance для агента | `vercel agent` |
| искать project-relevant agent skill снаружи | `vercel skills [query] --json` |
| вручную настраивать Vercel MCP | `vercel mcp` |
| поднимать свой isolated runner | `vercel sandbox` |
| искать agent execution в общих logs | `vercel agent-runs` |
| собирать deployment tracing вручную | `vercel traces`, `vercel metrics` |
| писать auth wrapper к Vercel API | `vercel api ENDPOINT` |

При обнаружении агента CLI по умолчанию non-interactive. Точный contract и
mutation surface каждой семьи принадлежат live help:

```bash
vercel --help
vercel help COMMAND
```
