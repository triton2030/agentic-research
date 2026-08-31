# Трасса решений

## Граница трассы

Параллельные окна не имеют честного общего порядка, поэтому ниже разделены main-window и scout-последовательности. За «открытие» считается чтение содержимого, а не `rg --files`.

В path-разделах `project/` означает `/Users/triton/Documents/GitHub/agentic-research/skills/1instruction-authoring/recheck-2026-08-30/probe-fixture/project/`.

## Общий main-window prefix до первого path-решения

1. `skills/shared/1instruction-authoring/portable/SKILL.md`
2. `/Users/triton/.codex/skills/1chat-recall/SKILL.md`
3. `_ops/product-frames/agentic-research.md`
4. `_ops/product-frames/agentic-research.principles.md`
5. `/Users/triton/.codex/skills/1chat-recall/references/retrieval.md`
6. `skills/shared/1instruction-authoring/portable/references/intent.md`
7. `/Users/triton/.codex/skills/1orchestration/SKILL.md`
8. `/Users/triton/.codex/skills/1orchestration/references/orient.md`
9. `/Users/triton/.codex/skills/1orchestration/references/brief.md`
10. `/Users/triton/.codex/skills/1orchestration/references/shape.md`
11. `/Users/triton/.codex/skills/1orchestration/references/assign.md`
12. `_ops/chat-recall/2026-08-19-020820-claude-7658d2a8.md`
13. `_ops/chat-recall/2026-08-28-193846-claude-76aa0843.md`
14. `_ops/chat-recall/2026-08-28-053552-claude-9bb215e3.md`
15. `_ops/chat-recall/2026-08-28-193846-claude-76aa0843.md` повторно, с номерами строк
16. `skills/1instruction-authoring/recheck-2026-08-30/probe-fixture/REQUEST.md`
17. `skills/1instruction-authoring/recheck-2026-08-30/probe-fixture/project/AGENTS.md`
18. `skills/1instruction-authoring/recheck-2026-08-30/probe-fixture/project/README.md`
19. `skills/1instruction-authoring/recheck-2026-08-30/probe-fixture/project/_ops/product-frames/pricing.md`
20. `skills/shared/1instruction-authoring/portable/references/zones.md`
21. `skills/shared/1instruction-authoring/portable/agents/zone-scout.md`
22. `_ops/chat-recall/2026-08-30-130004-codex-01a051ac.md`

Маршруты chat-recall до решения: основной запрос о распределении правил без дублирования; фасет на языке fixture про frontend/backend/README и canonical truth; тот же claim с `--since 2026-08-29`. Применимая позиция владельца подтверждена `_ops/chat-recall/2026-08-28-193846-claude-76aa0843.md:21,32-33`; более новой отмены не найдено.

## Путь 3: человек редактирует README onboarding

Первое решение было принято сразу после общего prefix: `project/AGENTS.md` — `no-change`; добавлять README-правило некуда и незачем.

После первого решения README-scout для coverage открыл по порядку:

1. `skills/shared/1instruction-authoring/portable/agents/zone-scout.md`
2. `project/AGENTS.md`
3. `project/README.md`
4. `project/_ops/product-frames/pricing.md`
5. `project/specs/analytics.md`
6. `project/specs/pricing.md`
7. `project/frontend/AGENTS.md`
8. `project/backend/AGENTS.md`

Coverage: весь fixture; ссылок на README/onboarding из других файлов нет. Gap: fixture не называет канонический источник точных install/server команд, если будущая правка их добавит.

## Путь 1: агент меняет подпись цены в frontend

После общего prefix main window открыл:

1. `project/frontend/AGENTS.md`
2. `project/backend/AGENTS.md`

Frontend-scout затем открыл по порядку:

1. `skills/shared/1instruction-authoring/portable/agents/zone-scout.md`
2. `project/AGENTS.md`
3. `project/frontend/AGENTS.md`
4. `project/specs/analytics.md`
5. `project/specs/pricing.md`
6. `project/_ops/product-frames/pricing.md`
7. `project/backend/AGENTS.md`
8. `project/README.md`

После его отчёта main window открыл:

1. `project/specs/pricing.md`
2. `project/specs/analytics.md`
3. `skills/shared/1instruction-authoring/portable/references/placement.md`

Первое решение: изменить только `project/frontend/AGENTS.md`, заменив безусловное чтение всех specs условным маршрутом к применимым specs и явным маршрутом price-label → `specs/pricing.md`.

Coverage: ближайшая instruction-chain, все specs и переданные соседние зоны проверены; цепочка `frontend/AGENTS.md` → `specs/pricing.md` → `_ops/product-frames/pricing.md` подтверждена. Gap: в fixture нет frontend-кода, исходной строки и точного допустимого старого названия.

## Путь 2: агент меняет backend schema

К общему prefix и двум затем открытым folder instructions добавилась backend-scout последовательность:

1. `skills/shared/1instruction-authoring/portable/agents/zone-scout.md`
2. `project/AGENTS.md`
3. `project/backend/AGENTS.md`
4. `project/_ops/product-frames/pricing.md`
5. `project/specs/analytics.md`
6. `project/specs/pricing.md`
7. `project/frontend/AGENTS.md`
8. `project/README.md`

Первое решение: `project/backend/AGENTS.md` — `no-change`. Единственное подтверждённое ребро — уже записанное условие `schema/**` → `make schema-check` до изменения. Перенос проверки на «после» не подтверждён.

Coverage: весь fixture и каждая переданная соседняя зона проверены. Gap: нет `Makefile`, `schema/**`, schema-owner, post-change validator или доказанного внешнего потребителя.

## Полнота runtime и probe

После первых path-решений main window по порядку открыл оставшиеся стадии полного official package: `references/wording.md`, `references/assembly.md`, `references/budget.md`, `references/probe.md`, `references/finish.md`. Вместе с уже открытыми `SKILL.md`, `references/intent.md`, `references/zones.md`, `references/placement.md` и `agents/zone-scout.md` это полное coverage current official package.

Fresh wording-probe сначала опроверг строку, где «только» можно было понять как запрет читать код и тесты. Повторная проба подтвердила одно чтение финальных двух строк: «только» ограничивает выбор внутри `specs/`, а price-label задача обязана открыть `specs/pricing.md`.

Matched probe открыл baseline-цепочку `AGENTS.md` → `frontend/AGENTS.md` → `specs/analytics.md` → `specs/pricing.md` → `_ops/product-frames/pricing.md`; candidate-цепочка открыла `AGENTS.md` → `frontend/AGENTS.md` → `specs/pricing.md` → `_ops/product-frames/pricing.md`. Обе запретили новое название. Обозреваемый diff временных деревьев содержал только `frontend/AGENTS.md`.

Probe-gap: порядок чтения возвращён самими clean агентами, а не независимой телеметрией. Long-trajectory retention, frontend-файловая правка, backend- и README-кандидаты не пробировались. Fixture, official package и итоговые канонические адреса не изменялись.
