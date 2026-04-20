# pitch-coherence-audit (Codex)

Codex-нативная версия `pitch-coherence-audit`. Claude Code-версия — в
соседней папке `projects/business/pitch-coherence-audit--skill-claude-code/`.

Итеративный аудит инвесторских питч-материалов — deck, memo, script.
Вызывается часто во время работы над контентом: после правок текста,
смены структуры слайдов, правок дизайна.

## Отличия от Claude Code-версии

- Нет `AskUserQuestion`. Недостающий контекст запрашивается обычным
  промптом к пользователю — одним сообщением с тремя короткими вопросами,
  не интерактивным виджетом.
- `pitch-context.md` в Codex-версии опционален: если файл уже есть, он
  читается; если нет и запись неуместна, контекст можно держать в рамках
  текущего аудита без записи на диск.
- Добавлен `agents/openai.yaml` — interface для Codex, `$pitch-coherence-audit`
  как default prompt trigger.
- Триггеры в `description` включают `$pitch-coherence-audit` — явное
  обращение к скиллу из Codex CLI.
- Аудит идёт по одному текущему pitch target за раз. Если пользователь
  дал папку, сначала сужать её до canonical/current материалов, а не
  смешивать драфты и экспорты в один verdict.
- Остальное — та же rigid structure, те же шесть осей, тот же ledger,
  тот же `references/stage-criteria.md`.

## Установка

```bash
cp -R projects/business/pitch-coherence-audit--skill-codex/ ~/.codex/skills/pitch-coherence-audit/
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py ~/.codex/skills/pitch-coherence-audit/
```

В installed version идёт только `SKILL.md`, `agents/openai.yaml`,
`references/`. `README.md` остаётся в репо.

## Файлы

- `SKILL.md` — тонкое ядро, тип rigid review.
- `agents/openai.yaml` — Codex interface + allow_implicit_invocation.
- `references/stage-criteria.md` — планка осей по стадии инвестора.
