# Проверка candidate — дешёвый фоновый Retrieval subagent

Статус: `installed 2026-08-31`. Владелец безусловно одобрил эти exact bytes
(`_ops/chat-recall/2026-08-31-160900-claude-eae04032.md#L16`), после чего они
записаны в оба tracked owner-а и в обе живые проекции без изменений; снимок
установленного пакета — `versions/installed-2026-08-31-background-subagent/`.

Проверка после установки: tracked claude 111/111, tracked codex 114/114, живой
`~/.codex/skills/1chat-recall` 114/114; все внутренние ссылки обоих пакетов
разрешаются; состав и содержимое обеих проекций побайтно равны утверждённому
кандидату.

## Входы и решение

- Новая коррекция владельца: [holder](../../../../_ops/chat-recall/2026-08-29-150002-codex-01a04cf3.md#L33).
- Сохраняемая форма: [один важный неблокирующий subagent](../../../../_ops/chat-recall/2026-08-25-215514-codex-01a039d8.md#L24).
- Текущий baseline `1skill-creation/SKILL.md`:
  `1831f5d21ef22ca9618a8211bb999f3c37bf663db805d08dc3732edfda15c7de`.

Это узкий repair уже проверенного пакета, а не новый продуктовый refactor:
основной retrieval и one-subagent topology сохранены. Единственная смысловая
дельта — `можно передать` заменено на обязательный дешёвый background dispatch
для важной темы; недоступный дешёвый executor не заменяется дорогим.

## Замороженные candidate bytes

| Runtime | Files | Manifest SHA-256 |
| --- | ---: | --- |
| [Codex candidate](../../versions/candidate-background-subagent-2026-08-31/codex/SKILL.md) | 20 | `a43b5939fab60d8bd44dc7afff03e15966cac604d30654940a1d0a5c8139e3e6` |
| [Claude candidate](../../versions/candidate-background-subagent-2026-08-31/claude/SKILL.md) | 21 | `f3d30aa9dfbf22145ce0e207755ded46f9358d8356389a4ea24560b4f71b0dd2` |

От installed baseline отличаются только `references/retrieval.md` и
`tests/test_chat_capture.py` в обоих runtime, плюс у Claude добавлен `Agent` в
его уже существующий `allowed-tools`. Candidate не содержит cache/bytecode.

### Active set изменённого места

В момент шага 4 Retrieval агент держит 15 самостоятельных единиц: 1 цель,
4 уникальных retrieval-boundary и 10 единиц самого background-решения
(важность, primary-first, один дешёвый dispatch, runtime adapter, nonblocking,
brief boundary, query inputs, metadata output, root reread и честный
cheap-unavailable fallback). Параметры `agent_type`/`fork_turns` у Codex и
`subagent_type`/`context: fork` у Claude поясняют один и тот же adapter action,
а не создают стадии. Это ниже ориентиру 20; Capture, Integrity и остальные
Retrieval шаги не менялись.

## Проверки exact bytes

| Проверка | Codex | Claude |
| --- | --- | --- |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | 114/114 | 111/111 |
| `ruff check --no-cache --select E,F --ignore E501 scripts tests` | pass | pass |
| `python3 -m compileall -q scripts tests` с отдельным cache | pass | pass |
| `md check --paths candidate --json` | 8 targets, 0 issues | тот же candidate check |
| `md check --paths work --json` | 3 targets, 0 issues | тот же work check |

Contract-test фальсифицирует прежнюю дырку: не проходит без точного mandatory
«ровно одного дешёвого», nonblocking lifecycle, corpus-only brief,
address/date/age/gaps, root reread и отказа от дорогой подмены. Он также
проверяет runtime delta: Codex `spawn_agent` с isolated `fork_turns: "none"`;
Claude background `Agent`, который действительно разрешён его frontmatter.

Локальная capability-проверка подтвердила, что Claude CLI умеет background
sessions и model selection (`claude --help`, `claude agents --help`), а Codex
текущего runtime предоставляет native `spawn_agent` и выбор model. Concrete
model ID намеренно не записан: модель и цена зависят от текущей конфигурации;
контракт требует явного выбора самой дешёвой доступной.

## Остаточный риск

Этот цикл не запускал реального background job: он проверяет пакет и его
runtime seams без новой волны субагентов, потому что владелец ограничил такие
волны двумя. Первое реальное важное Retrieval должно оставить наблюдаемый trace
dispatch → основной ход продолжился → вернулись новые address/date/age/gaps →
root перечитал holder. Если дешёвый profile окажется недоступным, честный gap
является предусмотренным результатом, а не поводом молча тратить дорогую модель.
