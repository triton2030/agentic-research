# Design — Инвентарь Claude Code

Снимок на 15 апреля 2026.

## Что Есть

### design-auditor
- Тип: plugin
- Источник: наш
- Что делает: структурированный визуальный аудит по пяти линзам качества (5 субагентов)

### playwright-skill
- Тип: skill
- Источник: наш
- Что делает: проверка интерфейса в живом браузере, снимки реального состояния

### screenshot-design
- Тип: skill
- Источник: наш
- Что делает: жёсткий screenshot-first визуальный аудит с обязательным Visual Evidence Ledger

## Чего Не Хватает

- frontend-skill — создание выразительных интерфейсов с акцентом на композицию, ритм и motion
- impeccable — премиальный уровень визуального качества (установлен, но привязан к другому проекту)
- web-design-guidelines — проверка UI-кода на соответствие web interface guidelines
- agent-browser-verify — быстрый визуальный sanity check после запуска dev server
- Figma MCP — реализация дизайна из Figma, связка компонентов, дизайн-система, генерация экранов
- Design plugin (Anthropic) — дизайн-критика, UX writing, accessibility audit
- Frontend Design plugin (Anthropic) — сборка интерфейса с design framework
- Нативная работа внутри Figma как основной среды
- Переносимый формат дизайн-правил (типа DESIGN.md)
- Память о дизайн-правилах между сессиями
- Design agent верхнего уровня для оркестрации генерации, критики и памяти
