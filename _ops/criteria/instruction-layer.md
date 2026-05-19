# Instruction Layer Criteria

## Зона ответственности

Когда работа меняет формулировку или placement текста инструкций:
`AGENTS.md`, root/subtree instructions, wording routing, precedence prose,
criteria links, links-over-inline или fresh-session language quality.

## Цель

Инструкционный текст помогает будущей модели правильно понять поведение в
нужный момент: без lost-in-middle, буквального применения частного примера,
случайного Hyrum-контракта, сикофантного frame capture и копирования criteria.

## Критерии

Rule: Каждое новое правило имеет одну owner surface; root-инструкции держат цель, routing и invariants, а не тела скиллов.
Why: Skill body грузится в нужный момент и сильнее root-текста при конфликте, а дубли правил становятся drift.

Rule: Перед записью инструкции `1instruction-layer` проектирует delivery: behavior target, named language failure, moment of need, owner surface и validation path.
Why: User signal: после split этот скилл отвечает за то, чтобы LLM правильно поняла формулировку инструкции, а не за весь системный контракт проекта.

Rule: В instruction-layer можно использовать профессиональные сокращения вроде SoT, RACI/DRI, RAID, blast radius, DoR, Go/No-Go, ADR/RFC и Poka-yoke только как сжатие понятного сильной модели паттерна.
Why: User signal: пользователь хочет убирать лишние объяснения за счёт терминологии из менеджмента и agent-system design, но не превращать инструкции в декоративный жаргон.

Rule: Для Codex поверхности Claude всегда только для чтения: `CLAUDE.md`, `.claude/**`, Claude skills и инструкционные файлы Claude.
Why: User signal: Codex не должен менять файлы, скилы и инструкции Claude; это жёсткая граница владельца против рассинхронизации между агентами.

Rule: Instruction files ссылаются на применимые `_ops/criteria/*.md`, а не копируют criteria-текст или protocol внутрь себя.
Why: Criteria и protocol должны иметь живых владельцев, иначе слои начнут расходиться.

Rule: Аудит instruction-layer работы проверяет language-quality chain: формулировка правила → правильный skill/criteria link → понятный handoff/stop.
Why: После split системную связку instructions → criteria → hooks → review держит `1folder-contract`, а этот файл защищает именно модель-читателя от плохой прозы.

Rule: Файл, который объясняет агентную систему пользователю, строится как «цитата пользователя» и затем «Текущие решения» по каждому пункту.
Why: Пользователь хочет видеть связь своей проблемы с текущим подходом без ощущения, что проблемы уже окончательно решены.

Rule: Instruction routing показывает platform-specific skill differences только там, где они реально меняют вызов; общий surface split держит `planning-surface-ownership`.
Why: Codex и Claude могут иметь разные live skill handles, но shared content не должен дублировать planning-owner правила.
