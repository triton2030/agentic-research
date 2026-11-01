---
description: "Semantic owners and projection contracts for cross-runtime skills."
---

# Shared Skill Owners

Реестр владельцев: где живёт исходник пакета и как он доставляется.
Что пакет делает, говорит его `SKILL.md`; реестр это не пересказывает —
пересказ устаревает молча.

## Правила

- Правка начинается с владельца. `skills/{claude,codex}/<имя>/` — tracked
  projections, `~/.{claude,codex}/skills/<имя>/` — установленные; их
  не правят напрямую.
- Общий пакет — `skills/shared/<имя>/portable/`. Runtime-дельта Codex —
  `platforms/codex/agents/openai.yaml`, только UI metadata.
- Reference-файл живёт ровно у одного владельца; соседи ссылаются на него.
- История пакета — `skills/<имя>/`.

## Общие owners

Владелец — `skills/shared/<имя>/portable/`, доставка — общий скрипт ниже.

| Пакет | Примечание |
| --- | --- |
| `112-learning-mode` | истории нет |
| `123-explain` | истории нет |
| `1agent-steering` | |
| `1code-router` | до 2026-10-30 — `1readable-code` |
| `1deep-agents` | |
| `1docs-write` | |
| `1document-system` | |
| `1folder-tree` | |
| `1goal` | |
| `1google-drive-archive` | |
| `1illustrations-and-charts` | |
| `1instruction-authoring` | |
| `1local-rules` | |
| `1md-search` | |
| `1product-shaping` | |
| `1skill-creation` | |
| `1use-principles` | |
| `1work-artifacts` | |
| `1write-as-me` | истории нет; образцы стиля — `_workspace/work-artifacts/2026-10-29-стиль-письма-владельца/` в Subfrost |
| `1writing-rule` | |

## Раздельные runtime owners

| Пакет | Владельцы | Доставка |
| --- | --- | --- |
| `1t3` | `skills/claude/1t3/`, `skills/codex/1t3-codex/` | общий скрипт по имени каждого |
| `1orchestration` | `skills/{claude,codex}/1orchestration/` | общий скрипт |
| `1fresh-eyes` | `skills/{claude,codex}/1fresh-eyes/`; продуктовая пара — у Claude owner, не устанавливается | явный manifest из `skills/1fresh-eyes/`; профиль `agents/expansionist.{md,toml}` ещё и в `~/.{claude,codex}/agents/` |
| `1smart-simple` | tracked owner нет: правда — `~/.{claude,codex}/skills/1smart-simple/` | вручную |

## Product owners

`1chat-recall/` и `1handoff/` здесь владеют только продуктовой парой
`product-frame*.md`; поведение — у их runtime `SKILL.md`. Runtime-деревья
`1chat-recall` расходятся намеренно (`allowed-tools`, переменные сессии,
пути, имя агента, тесты): правь оба адресно, файлы между ними не копируй —
копия runtime-теста уже стирала проверки Codex.

## Сняты

- 2026-10-30, переход на плагин `mattpocock-skills`[^matt]: `1planning` →
  `/to-spec`, `/to-tickets`, `/wayfinder`; `1interview-tool` →
  `/grill-with-docs`, `/grill-me`, `/to-questionnaire`; `1context-refactor` →
  `/retro`; `1findings`.
- `1hermes` — 2026-10-21, `1index` — 2026-10-24.

История каждого — `skills/<имя>/`.

[^matt]: [Слова владельца, 2026-10-30](../../_ops/chat-recall/2026-10-30-143023-claude-20b43aed.md#recall-a4f0045b2c6f4cd783ba8618dd356655).

## Синхронизация

```bash
python3 skills/shared/sync_simple_projections.py <имя> [<имя> …] --write --install
python3 skills/shared/sync_simple_projections.py <имя> [<имя> …] --check
```

Скрипт собирает все portable-файлы и непересекающуюся runtime-дельту.
Лишние файлы в проекциях он не удаляет: их происхождение сначала решают
явно. Special-manifest скрипт `1skill-architect/sync_projections.py` выведен
из обращения и лежит в `skills/1skill-architect/shared-owner-2026-08-08/`.
