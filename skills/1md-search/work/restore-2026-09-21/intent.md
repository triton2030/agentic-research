---
description: "Граница и основания переработки 1md-search от 2026-09-21."
---

# Заказ

Проверить код md-tools, полностью переписать скилл поиска по эмбеддингам
и восстановить автоматическое подключение. Исполнители — Sol medium.
Слова владельца: текущий разговор и
`/Users/triton/Documents/My_projects/md-tools/_ops/chat-recall/2026-09-21-223200-codex-01a0c503.md`.

Функция скилла — находить неизвестный Markdown по смыслу и приносить
прочитанные адресуемые фрагменты для исходной задачи. Полная переработка
меняет форму всего пакета, сохраняя границы данных, разрешения, различие
кандидата и доказательства, проверку покрытия и восстановление индекса.

Исходник: `skills/shared/1md-search/portable/`; runtime metadata —
`skills/shared/1md-search/platforms/codex/agents/openai.yaml`.
Снимок до изменений: `../../versions/before-2026-09-21/`.
Существующие проекции Codex и Claude доставляются штатным sync.

## Стадия

Переработаны основной текст, три references и metadata. Три свежих Sol medium
проверили смысл, необходимость требований и исполнимый маршрут. Исправлены
две потери: доступный exact/filesystem fallback без разрешения на embedding
и первый запрос при неизвестном языке источников. Изолированная проба прошла
cold index → dry-run/confirm → FRESH → dense search → body read.

Canonical portable и Codex metadata доставлены штатным sync в tracked и
installed Codex/Claude projections; byte parity и skill validation прошли.
Автоматический вызов разрешён. Существующий backend сохранён; локальный E5
проверен отдельно и не выбран новым default без решения владельца.
