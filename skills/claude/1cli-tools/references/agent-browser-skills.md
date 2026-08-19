---
description: "Version-matched skills active agent-browser 0.34.0."
---

# agent-browser: Bundled Skills

Момент: выбирается workflow до первой команды `agent-browser`. Сверено
2026-08-19 с active `agent-browser 0.34.0`; быстрее всего меняется список skills.

## Дельта

CLI сам поставляет инструкции, совпадающие с его версией:

```bash
agent-browser skills get core --full
agent-browser skills list --json
agent-browser skills get NAME --full
```

| Новый route | Что он уже содержит |
|---|---|
| `derive-client` | HAR → прямой client/CLI для повторяемого сайта |
| `dogfood` | exploratory QA с screenshots, video и repro evidence |
| `electron` | CDP workflow для Electron apps |
| `slack` | Slack browser workflow |
| `agentcore` | AWS Bedrock AgentCore cloud browser |
| `vercel-sandbox` | Chrome внутри Vercel Sandbox microVM |

Канонический владелец содержания — вывод `skills get`; этот файл хранит только
факт существования version-matched routes.
