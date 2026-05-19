# Business — Инвентарь

Снимок после cleanup 18 мая 2026.

Инвентарь фиксирует business-facing handles и gaps. Общие выводы не держать
здесь: promoted principles уходят в `knowledge/wisdom-*` или guides.

## Shared

### pitch-coherence-audit

- Тип: skill
- Источник: наш
- Где есть: Claude Code, Codex
- Что делает: проверяет investor pitch materials на нарративную связность и
  инвесторский посыл после правок.

## Claude Code

### playwright-skill

- Тип: skill
- Источник: наш
- Что делает: проверяет сайты, формы и клиентский опыт в живом браузере.

### xlsx

- Тип: skill
- Источник: Anthropic
- Что делает: читает, создаёт и редактирует Excel-таблицы.

### pdf

- Тип: skill
- Источник: Anthropic
- Что делает: читает, создаёт, объединяет и разделяет PDF.

### pptx

- Тип: skill
- Источник: Anthropic
- Что делает: создаёт и редактирует PowerPoint-презентации.

### docx

- Тип: skill
- Источник: Anthropic
- Что делает: создаёт и редактирует Word-документы.

## Codex

Пока отдельный business-facing слой тонкий: live Codex handle из этой категории
только `pitch-coherence-audit`.

## Missing

- Codex-совместимые business skills beyond `pitch-coherence-audit`.
- Автоматизации и регулярные проверки.
- Документооборот для Codex: `xlsx`, `pdf`, `docx`.
- Notion / CRM / почта / календарь / BI / support connectors.
- Рекламные кабинеты, платежи, финансы, звонки и расшифровки.
- GitHub, Vercel и Build Web Apps plugin-layer для связки бизнес-решений с
  продуктом.
