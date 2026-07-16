# Business — Инвентарь

Снимок после cleanup 14 июля 2026.

Инвентарь фиксирует business-facing handles и gaps. Общие выводы не держать
здесь: promoted principles уходят в `knowledge/wisdom-*` или guides.

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

Отдельного business-facing skill сейчас нет. Business-задачи идут через owner
конкретной работы и установленные document/data/plugin surfaces.

## Missing

- Codex-совместимый business skill с доказанным повторяемым workflow и owner.
- Автоматизации и регулярные проверки.
- Документооборот для Codex: `xlsx`, `pdf`, `docx`.
- Notion / CRM / почта / календарь / BI / support connectors.
- Рекламные кабинеты, платежи, финансы, звонки и расшифровки.
- GitHub, Vercel и Build Web Apps plugin-layer для связки бизнес-решений с
  продуктом.
