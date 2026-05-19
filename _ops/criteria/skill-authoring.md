# Skill Authoring Criteria

## Зона ответственности

Когда работа создаёт, переписывает или проверяет `SKILL.md`, trigger
description, `agents/openai.yaml`, skill references или границы между скиллами.

## Цель

Скилл должен быть коротким, outcome-first и вызываться в нужный момент без
старого process-heavy поведения.

## Критерии

Rule: `description` front-loads when/skip boundaries, а body задаёт outcome, constraints, evidence, output и stop rules.
Why: Сильные модели сначала видят trigger surface; им нужен короткий контракт, а не длинный process stack.

Rule: Model-delta правка удаляет или сужает старое process-heavy правило, а не добавляет новый слой поверх него.
Why: Иначе live skill одновременно тянет модель к GPT-5.5 outcome-first контракту и к старому defensive process.

Rule: Tool-specific детали живут в tool descriptions или runtime metadata, а reasoning effort не повышается как первая починка.
Why: Сначала чинятся цель, критерии, ограничения, validation и stop rules; tool surface отвечает за свои детали.

Rule: Новый скилл создаётся только для повторяемого workflow с отдельным trigger.
Why: Иначе skill landscape разрастается как каталог идей, а не как рабочая система.

Rule: Официальный минимум Codex-скилла — директория с `SKILL.md`, где есть `name` и `description`; `scripts/`, `references/`, `assets/` и `agents/openai.yaml` добавляются только по функции.
Why: Отсутствие optional surface само по себе не значит, что скилл сломан.

Rule: Если `agents/openai.yaml` нужен для UI, policy, MCP dependencies или discoverability, он создаётся или синхронизируется с `SKILL.md`.
Why: `agents/openai.yaml` — реальная metadata/policy surface, но не обязательный файл.

Rule: Крупная правка или создание Codex-скилла сверяется с текущими официальными OpenAI Agent Skills docs.
Why: Пользователь заметил риск писать Codex skills из локальной логики без актуального официального baseline.

Rule: Для global Codex skill discoverability проверять live-root `/Users/triton/.codex/skills/<name>` и совместимый `$HOME/.agents/skills/<name>`.
Why: Runtime-факт и официальный/совместимый authoring path могут различаться.

Rule: `UserPromptSubmit` — threshold-based intent-grounding только на 1-м ходу сессии; substantive write-gate реализован отдельным `PreToolUse` hook (`criteria-gate.py`), который требует prior Read из applicable `_ops/criteria/*.md`. `1work-review` skill body владеет verbatim citation requirement в Output template; `Stop` hook больше не дублирует эту проверку.
Why: Прежний UserPromptSubmit reminder был декоративным после 1-го хода; real gate в PreToolUse даёт structural enforcement, skill body — substance проверка, hook — детектор структурного факта без cognitive work.

Rule: Hooks детектируют структурные факты (file change, criteria edit, anchor read), cognitive work (citation, classification, decision) живёт в skill body; hook лишь композирует — делегирует skill через directive injection или session-state check, не дублирует логику.
Why: Hook проверки на substance (verbatim quote, marker presence) деградируют в ритуал — сильная модель учится cargo-cult'у вместо понимания; разделение detect-vs-decide сохраняет skills как локус знания и hooks как локус принуждения для inviolable invariants.

Rule: Skills с auto-fire на структурный факт (например, `1work-review` после substantive write, `1user-truth` при правке `_ops/criteria/*.md`) держат явные auto-fire phrases в frontmatter description вместе с manual trigger words; trigger surface должен включать обе категории.
Why: Hook composability через skill invocation надёжна только когда trigger surface skill распознаёт structural-fact фразы из description; без auto-fire phrases skill требует manual prompt пользователя.

Rule: Дублирование одного правила в нескольких `SKILL.md` может быть полезным freshness mechanism; не сводить его агрессивно к shared reference.
Why: Главный failure mode иногда не drift, а то, что нужный скилл не триггернулся и правило не дошло до агента.

Rule: Для Claude `SKILL.md` применять Opus 4.7 prompt practices; для Codex/GPT-5.5 — outcome-first контракт без long process stack.
Why: Тело скилла является prompt для модели; mixed-runtime skill должен держать нижний bound по обеим рамкам.

Rule: Claude-facing `description` держать < 1024 символов, считать `wc -m`; при росте выше 900 или системной правке делать batch-sweep по `SKILL.md`.
Why: Anthropic loader может молча обрезать хвост, а aggregate drift не виден из одной правки.

Rule: При создании или правке Codex skills учитывать visibility budget: `name` до 64 символов, `description` до 1024 символов, первый смысл front-loaded.
Why: Codex сначала видит только `name`, `description` и путь; размытая metadata мешает выбору скилла.

Rule: Reference-файлы скилла хранят только decision-changing детали; официальные docs и внешние источники сжимаются до полезных примитивов.
Why: User signal: пользователь хочет, чтобы скиллы не учили языковую модель очевидному, а давали ей самые важные инновации, ограничения и полезные возможности из документации.

Rule: UI-facing `display_name` / Label для Codex skills должен оставаться английским handle-подобным именем, а не русским псевдонимом.
Why: User signal: русские отображаемые имена скиллов в интерфейсе путают пользователя, потому что сами скиллы фактически называются на английском.

Rule: Chat-facing service labels in `SKILL.md` output templates stay stable English or handle-like; explanatory prose can follow the chat language.
Why: User signal: русские chat labels тоже путают пользователя, потому что они маскируют реальные английские названия и служебные метки скиллов.

Rule: Criteria про русский human-facing текст не применяются к skill handles, `display_name`, metadata keys, command names, template field labels или status labels.
Why: Иначе соседние критерии про удобочитаемые русские документы снова начинают конфликтовать с английской идентичностью скиллов и служебных меток.

Rule: Codex skill `description` trigger phrases пишутся на языке пользователя проекта; для русско-говорящего пользователя — RU-primary (фразы которые пользователь реально печатает). Skill handles (`$1strategy`), `display_name`, и technical concept anchors остаются английскими: specification literalism, Owner Decision Map, OODA, one-way/two-way doors, lost-in-middle, DDD bounded contexts, defense in depth, leverage point, premortem, adversarial self-play, Hyrum unintentional contracts, ground-check.
Why: User signal (2026-05-19): «я работаю с этими скилами на русском языке и триггеры должны быть на русском». English-only triggers вызывают undertriggering — matcher не видит фразы которые пользователь реально печатает. English identity скилов и устойчивых терминов сохраняется для cross-runtime portability и связи с canonical literature.

Rule: Codex-скилл для субагентов явно говорит: это нативный механизм Codex, не CLI/MCP, и запуск требует прямого запроса или подтверждения брифа.
Why: User signal: пользователь исправил `1fresh-eyes`, чтобы субагенты не вызывались через внешний обход или без разрешения.
