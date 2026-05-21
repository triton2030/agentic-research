# Hooks Runtime Guardrails

Практический guide: когда hooks стоит делать, когда они реально защищают
работу агента, а когда становятся шумом и скрытой логикой.

## Смысл

Hook — это заранее выбранная точка жизненного цикла, где система запускает
детерминированный обработчик: скрипт, HTTP endpoint, MCP tool или другой
handler. Хороший hook не просит модель “помнить правило”, а ставит проверку в
момент, где нарушение видно по фактам: перед инструментом, после инструмента,
при старте сессии, при отправке запроса или перед финалом.

Общий паттерн старый: WordPress описывает hooks как предопределённые места, где
один кусок кода может расширить или изменить другой; Git запускает hooks на
событиях репозитория; pre-commit использует их, чтобы ловить простые проблемы
до review. В агентных системах смысл тот же, но риск выше: hook работает внутри
agent loop и может влиять на действия модели.

## Когда Hooks Максимально Полезны

- Есть повторяемый сбой в конкретном lifecycle moment: до записи, после записи,
  перед финалом, при старте, при запросе разрешения.
- Проверка детерминированная: путь файла, команда, exit code, JSON-поле,
  наличие незакрытой проверки, список изменённых файлов.
- Ошибка дорогая или часто повторяется, а текстовая инструкция уже не держит
  поведение.
- Hook можно протестировать отдельно: подать JSON на stdin, увидеть stdout /
  stderr / exit code, проверить лог.
- Hook короткий, idempotent и не требует скрытого человеческого контекста.
- Есть понятный owner: какой файл объявляет hook, где лежит script, кто
  проверяет, когда выключить или пересмотреть.

Хорошие примеры:

- `UserPromptSubmit`: короткий intent-first якорь или предупреждение о явном
  user-only gap.
- `SessionStart`: лёгкая ориентация по проекту или загрузка малого, свежего
  контекста.
- `PreToolUse`: запрет опасной команды, записи в защищённый путь или утечки
  секрета.
- `PostToolUse`: форматирование, narrow lint, анализ вывода инструмента.
- `PermissionRequest`: внешний approval path или auto-allow только для узких,
  проверяемо безопасных действий.
- `Stop`: финальная проверка после правок, защита от преждевременного “готово”.
- `pre-commit`: простые style/secret/debug checks до code review.

## Когда Hooks Не Нужны Или Мешают

- Правило редкое, смысловое или требует judgment. Тогда лучше skill, criteria,
  review или обычная инструкция.
- Hook грузит длинный context каждый turn. Это дешевле кажется, чем стоит:
  шумит, стареет и крадёт внимание модели.
- Hook дублирует owner: то же правило уже живёт в `AGENTS.md`, `SKILL.md`,
  criteria и validator без ясного главного источника.
- Hook скрывает control flow: агент и пользователь не понимают, почему действие
  изменилось, заблокировалось или повторилось.
- Проверка медленная или flaky на горячем пути. Долгие тесты лучше запускать
  явно, в фоне или на CI, если hook не обязан блокировать.
- Нужна настоящая policy enforcement, а hook локальный и отключаемый. Git docs
  предупреждают: client-side hooks не клонируются и не годятся как строгая
  политика; для enforcement нужен server-side / CI / permissions / sandbox.
- Hook претендует на security boundary. Codex docs прямо называют `PreToolUse`
  guardrail, не полным enforcement: покрытие tool paths может быть неполным.
- Hook запускает произвольный shell с текущими credential-ами без review,
  абсолютных путей, input validation и безопасного quoting.

## Как Проектировать

1. Назови failure class одним предложением: “агент финализирует после правок без
   проверки”, “агент пишет в `.env`”, “агент забывает стартовый маршрут”.
2. Выбери ближайший lifecycle moment. Не ставь global hook, если проблема
   возникает только в одном проекте или одном workflow.
3. Выбери самый слабый механизм, который реально держит правило:
   instruction < skill < validator < hook < permission/sandbox/CI/server policy.
4. Определи handler contract: входные поля, matcher, stdout JSON, stderr, exit
   code, timeout, что видит модель, что видит пользователь.
5. Сделай hook маленьким: no network by default, no long context dump, no broad
   filesystem scan, no hidden model call без причины.
6. Проверь безопасное исполнение: absolute paths, quoted variables, no path
   traversal, no sensitive files, predictable cwd.
7. Протестируй отдельно и через runtime UI: direct stdin JSON, syntax check,
   `/hooks` или equivalent trust/review flow, один positive и один negative
   case.
8. Запиши re-check signal: после Codex/Claude update, schema change, plugin
   change, noisy false positives или нового bypass path.

## Codex Notes

- Для Codex config использовать `[features].hooks = true`; `codex_hooks` только
  deprecated alias.
- Перед правкой hook config сверять текущие official docs/schema и локальный
  `codex features list`, потому что hook surface быстро меняется.
- Не считать `PreToolUse` полным enforcement boundary: Codex docs описывают
  неполное перехватывание shell/tool paths.
- Если в одном layer есть и `hooks.json`, и inline `[hooks]`, Codex их merge-ит
  и предупреждает; лучше один формат на layer.
- Matching hooks из нескольких sources запускаются все; higher-precedence
  config не заменяет lower hook declarations.
- Несколько command hooks одного event запускаются concurrently; один hook не
  может предотвратить старт другого matching hook.
- `UserPromptSubmit` и `Stop` matcher сейчас не используют; не проектировать
  тонкую фильтрацию через matcher для этих событий.
- Project-local hooks требуют trusted project `.codex/` layer.

## Decision Check

Перед новым hook ответь:

- Что именно должно стать невозможным или гарантированным?
- Почему это нельзя решить меньшим слоем?
- Где один owner этого правила?
- Как я докажу, что hook сработал и не шумит?
- Что произойдёт, если hook отключится, устареет или начнёт давать false
  positives?
- Это знание (как делать X — owner skill body) или инвариант (при условии Y
  запретить Z — hook)? Если знание — skill, не hook. Hook делает cognitive
  work (читай-проверь-классифицируй) только когда знание тоже у hook'а;
  иначе cognitive — в skill body, hook — детектор структурного факта.
- Hook stateless или нужна память сессии? Stateful enforcement (повторное
  чтение, проверка факта применения, threshold-based firing) — через
  shared session-state, не in-memory tracking, не через transcript re-parse
  каждый ход. Pattern: `~/.claude/state/session-{session_id}.json` + CLI
  `~/.claude/skills/1start-here/scripts/session-state.py`; schema —
  `~/.claude/skills/1start-here/references/session-state-schema.md`.
- Hook делает свою cognitive проверку или композирует skill? Composability
  паттерн: hook detect structural fact → inject directive «прогони skill X»
  → skill body владеет smysl'ом проверки. Hook не дублирует skill logic.

Если ответы размытые, hook преждевременен.

## Session-state pattern (baseline для stateful enforcement)

Hook без памяти сессии стреляет одинаково каждый ход — отсюда re-read одного
и того же criteria 5 раз, verbatim citation требуемая когда anchor docs не
менялись, маркеры ставимые ради маркеров. Session-state разрывает loop:

- **anchor_reads** — какие anchor-doc (`AGENTS.md`, `CLAUDE.md`, `_ops/GOAL.md`,
  `_ops/PROJECT-ROADMAP.md`, `_ops/project-graph.md`) прочитаны в этой сессии
  и когда (turn_id + ts + mtime).
- **file_changes** — что менялось в текущей и прошлых turns.
- **skill_invocations** — какие skills вызывались (per turn). Hook читает
  это для composability check: вместо `marker регex` спрашивает «вызывался
  ли skill реально».
- **markers_seen / applied_criteria** — substance level (skill записывает,
  hook читает).
- **turn_id** — threshold для «только первый ход» / «после N пропусков».

CLI: read / write / append / bump / sync-from-transcript / gc. Atomic
writes (temp + rename). Fail-open: ошибки никогда не ломают hook или skill.
GC: 14 дней.

Использовать когда: cross-hook / cross-skill ratio truth, idempotent
re-firing, threshold logic, mtime-based freshness, composability detection.
Не использовать как durable storage для user quotes (это
`_ops/user-said/YYYY-MM-DD.md` через `1user-said`) или для task contracts
(`_ops/plans/**/task-*.md` через `1planning`).

## Sources

- [OpenAI Codex hooks docs](https://developers.openai.com/codex/hooks)
- [Anthropic Claude Code hooks guide](https://code.claude.com/docs/en/hooks-guide)
- [Anthropic Claude Code hooks reference](https://code.claude.com/docs/en/hooks)
- [Anthropic Claude Code power user tips](https://support.claude.com/en/articles/14554000-claude-code-power-user-tips)
- [WordPress Plugin Handbook](https://developer.wordpress.org/plugins/hooks/)
- [Git book](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks.html)
- [Atlassian Git hooks tutorial](https://www.atlassian.com/git/tutorials/git-hooks)
- [pre-commit docs](https://pre-commit.com/)
