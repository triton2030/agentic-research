# Карта рефактора 1instruction-authoring v4

## Функция и утверждённый курс

Скил создаёт и устанавливает слой инструкций как минимальный граф доставки
внешней правды между зонами, а не как учебник ремесла зоны. Курс и terminal
outcome утверждены в
`_ops/chat-recall/2026-08-29-184951-codex-01a04dbd.md:15-16`.

Выбран тонкий маршрутизатор самостоятельных стадий. Условие чтения каждой
стадии живёт только в `SKILL.md`; ни один reference-файл не вызывает другой.
Локальные «Уникальный контекст» и «Цель» владеют выводимым поведением, а
hard-lines сохраняют authority, критический порядок и фальсифицирующую
приёмку.

## Поглощения и изменения

| Прежний смысл | Новый владелец | Изменение |
| --- | --- | --- |
| До 20 строк в каждом файле | `budget.md` | Считаются независимо нарушимые смыслы активной точки решения |
| Жёсткий символьный потолок цели и контекста | локальный commander intent | Полная однозначная мысль важнее числа символов |
| Reference-файлы вызывают следующие стадии | маршрут `SKILL.md` | References возвращают только собственный артефакт |
| Чтение зоны целиком | `zones.md` + `agents/zone-scout.md` | Независимый ограниченный поиск рёбер и coverage gaps |
| Candidate-пробник без baseline | `probe.md` | Единственная переменная — подключённое instruction tree целиком |
| Дублирующий surprise-самоотчёт до пробника | `intent.md` + `probe.md` | Admission оставляет абляцию и вред, причинность доказывает matched probe |
| Безусловная запись всех возможных проекций | `finish.md` | Устанавливаются только разрешённый owner и существующие проекции |

Корень-роутер, рёбра с моментами, один владелец, папка-склад, INDEX,
«Нерушимо:», полные предложения, независимый пробник и authority-gate
сохранены.

## Description surfaces

Instructional body `SKILL.md`, references и agent prompt написаны по-русски.
Frontmatter `description` и Codex `short_description` — короткие
English trigger-only строки. Codex `display_name` и `default_prompt` остаются
runtime metadata.

## Состав точного candidate

- portable: `SKILL.md`, восемь файлов `references/` и
  `agents/zone-scout.md`;
- Codex delta: `platforms/codex/agents/openai.yaml`.

Карта, `cut.md`, `goal-context.md`, `user-said.md` и отчёты проверок
остаются историей и в устанавливаемый пакет не входят.

## Gate установки

Gate пройден. Final literal и trajectory — PASS; clean controlled pair показал,
что candidate не создаёт недоказанные зонные правила там, где baseline их
создаёт. Exact candidate записан в shared owner, синхронизирован и установлен в
Claude и Codex; byte parity, ссылки, `qv-skill`, sync check и
`plugin-eval 100/100` прошли. Манифест 11 candidate-файлов:
`296a0b5677ec3fc24a625b0614ae5d6fd47b36b13bfbbd375b6543f3b75aec33`.
