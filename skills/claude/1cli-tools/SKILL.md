---
name: 1cli-tools
description: >-
  Use before a version-sensitive choice, helper, or recovery in active
  agent-browser, ast-grep, npm 12, uv, TypeScript 7, md, GitHub/Vercel CLI, or
  FFmpeg 9; also after updates or version conflicts.
---

# Свежие возможности CLI

Память модели старее инструментов на этом Mac. Знакомое имя не означает
знакомые возможности.

## Открой Один Reference В Текущий Момент

| Момент решения | Получить |
|---|---|
| выбрать workflow в `agent-browser` | [version-matched bundled skills](references/agent-browser-skills.md) |
| выбрать browser evidence/diagnostic | [встроенные diagnostics](references/agent-browser-diagnostics.md) |
| искать структуру или переписывать AST | [`ast-grep` 0.45](references/ast-grep.md) |
| npm install пропустил lifecycle script | [npm 12 allowScripts](references/npm-12.md) |
| проверить vulnerabilities изолированного Python CLI | [`uv tool audit`](references/uv-tool-audit.md) |
| пересобрать environment Python CLI | [`uv tool install --reinstall`](references/uv-tool-rebuild.md) |
| запустить глобальный TypeScript 7 | [новые compiler defaults](references/typescript-7.md) |
| работать с большим Markdown corpus | [локальный md-tools](references/markdown-knowledge.md) |
| работать с GitHub agent session | [`gh agent-task`](references/github-agent-task.md) |
| искать/обновлять GitHub agent skill | [`gh skill`](references/github-skills.md) |
| выбрать Vercel agent/platform route | [новые команды Vercel 59](references/vercel-agent-platform.md) |
| выбрать codec в локальном FFmpeg | [возможности active build](references/ffmpeg-build.md) |
| обновить конфликтующие active CLI | [owner и совместный smoke](references/runtime-update.md) |

## Вернись В Задачу

1. Сверь active version с live-help командой из reference; при drift live help
   побеждает. Project-local owner/config сильнее global.
2. Используй capability, если она меняет ход задачи. Discovery не разрешает
   mutation или network.
3. Верни `TOOL VERSION · capability → changed action` либо `no relevant delta`.
