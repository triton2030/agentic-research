---
description: "Version-matched skills active agent-browser 0.38.1."
---

# agent-browser: Bundled Skills

Момент: выбирается workflow до первой команды `agent-browser`. Сверено
2026-09-24 с active `agent-browser 0.38.1`; быстрее всего меняется список skills.

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
| `protected-vercel-deployments` | доступ к защищённому preview через текущую Vercel identity и короткоживущий OIDC token |
| `webmcp-gen` | создание и проверка экспериментальных WebMCP tools для workflow страницы |

Канонический владелец содержания — вывод `skills get`; этот файл хранит только
факт существования version-matched routes.
