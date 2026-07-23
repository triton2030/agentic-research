# Code locality hook removed — 2026-06-02

## Факты

- Удалён Claude `PreToolUse` hook `pre-tool-skill-code-locality.py`
  (`~/.claude/hooks/`) и снята его регистрация в `~/.claude/settings.json`.
- Хук стоял с 2026-05-22 (task-402) и блокировал запись под
  `~/.claude/skills/**` / `~/.codex/skills/**` вне declarative-whitelist
  (`SKILL.md`, `references/*.md`, `assets/*`, `agents/openai.yaml`,
  `scripts/` для `1start-here`/`1findings`).
- Снят по явному решению пользователя («снести целиком» после разбора
  альтернатив remove / relax / redirect).
- Инвариант сам по себе НЕ отменён: skill-папки остаются декларативными
  по соглашению (см. `experiments/md-embedding-server/README.md`, блок про
  skill folders). Снят только runtime-gate, не норма.

## Причина

- Хук дважды ложно блокировал read-only команды. Корень: write-детектор
  регуляркой `(?<!2)>>?(?!&)` ловил `>` внутри строковых литералов
  (`awk '/^description: >/'`), принимал за file redirect и блокировал все
  `skills/`-пути в составной команде, включая `ls -d ... /knowledge`.
  False-positive класс, перевешивает выгоду proactive-gate в solo-потоке.

## Источник

- Прошлый decision-record: `_ops/findings/_archive/2026-05-22-code-locality-hook.md`.
- Owner хука по заголовку файла: `1folder-contract` (task-402).

## Проверка

- `python3 -m json.tool ~/.claude/settings.json` → VALID; в `PreToolUse`
  остался только `md-graph-pre-edit-reminder.py`.
- Файл хука и его `.pyc` удалены (`GONE`).
- `find . -name "*skill-code-locality*"` в репо → пусто (копии в репо нет).
- Живой README сервера описывает норму, не enforcement → правки не требует.

## Что Снимет Находку

- Архивировать после коммита/пуша.
- Если решим снова усилить declarative-only — это решение `1folder-contract`,
  и тогда чинить регулярку write-детектора: не считать `>` в кавычках за
  redirect (точить через `shlex`-токенизацию, а не голый regex).
