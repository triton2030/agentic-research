# Чем проверен

## Lifecycle

`candidate → проверен поведением → спроецирован глобально`

Текущий статус: **candidate** — установлен глобально до поведенческой
проверки (осознанное решение кампании 2026-08-08, риск назван Codex-ревью).
Утверждение текста: «да» владельца в сессии 2026-08-08, дословные решения —
`_ops/chat-recall/2026-08-08-135005-claude-dfa9fb5c.md`.

## Support envelope

`Claude Opus 5` / `GPT-5.6` в Claude Code / Codex; вызов преимущественно
владельцем и через `1handoff` — длинная автономия не предполагается.

## Статус проверок — 2026-08-08

| Что | Как | Статус |
|---|---|---|
| Интервью владельца пройдено, «да» получено на состав | чат этой сессии | сделано |
| Текст против собственного аудита (`1skill-shaping/audit.md`) | 9 операций по черновику | сделано, находки в сдаче |
| Активация голой фразой | — | **не прогонялось** |
| Пять намерений на реальном INDEX этого репо | — | **не прогонялось** — у репо нет INDEX.md |
| Сравнение со старой версией на живой задаче | — | **не прогонялось** |

## Ближайшая проверка

Создать INDEX.md для этого репозитория новым скилом (после «да» владельца на
файл) и прогнать пять намерений из живых целей.

## 2026-08-29 — commander-intent refactor и установка

Owner evidence:
`_ops/chat-recall/2026-08-29-205016-codex-01a04e33.md:21,23`.

| Что | Evidence | Статус |
| --- | --- | --- |
| Exact candidate до owner/live | `candidate-2026-08-29/`; tracked owner оставался без diff до gate | pass |
| Независимый instruction acceptance | active sets: admission 14, writing 19, long-session upkeep 13, stale-route upkeep 12 | pass |
| Независимый trajectory review | fresh upkeep обязан пройти `admission → writing`; прямой upkeep только для ранее допущенного stale-route | pass |
| Trigger surfaces | frontmatter 126 символов; Codex short_description 125; обе English trigger-only `Use when…` | pass |
| Causal/behavioral fixture | `_workspace/1context-refactor-probe-2026-08-29/RESULT.md`; один оплаченный intent-route записан без копии решения | structural pass; probabilistic effect candidate |
| Установка | tracked owner → Codex/Claude tracked projections → `~/.codex/skills/1index` и `~/.claude/skills/1index` | pass |
| Validator и parity | `quick_validate.py` для owner и четырёх projections; `sync_simple_projections.py --check`; tracked/live directory diff | pass |
| Markdown edges | три связи body→reference прочитаны с обеих сторон; labels совпали с локальными Целями | semantic edge review pass for package scope |

Residual risk: один fixture показывает различающий structural route, но не
доказывает вероятностное улучшение cold-agent behavior на повторных прогонах.

## 2026-08-31 — восстановление содержательной цели

Owner correction:
`_ops/chat-recall/2026-08-29-205016-codex-01a04e33.md:31`.

Новый clean-room candidate возвращает три зонтичные цели, усиливает
`Уникальный контекст` и сохраняет однофайловую runtime-форму. Две независимые
волны проверили буквальное соблюдение и trajectory; realistic multi-source
holdout дважды прошёл без смысловых находок. Финальные точные байты после
line-only repair проверены основным агентом; подробный causal trace —
`review-2026-08-31/final-checks.md`.

Статус: **exact candidate ready for owner approval**. Tracked owner,
projections и live не менялись.
