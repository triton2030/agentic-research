# Trace

Три пути исследованы в одной сессии. Общая подготовительная
последовательность до их разбора: `candidate-v6/SKILL.md`,
`candidate-v6/agents/zone-scout.md`,
`candidate-v6/platforms/codex/agents/openai.yaml`,
`candidate-v6/references/verification.md`, `probe-fixture/REQUEST.md`, затем
`project/AGENTS.md`. Команда чтения локальных входов открыла по порядку
`project/frontend/AGENTS.md`, `project/backend/AGENTS.md`, `project/README.md`;
ниже отдельно указаны реально использованные адреса каждого пути до его
первого решения.

Независимый zone scout не запускался: frontend-владелец адресован действующей
цепочкой, backend содержит локальную hard line, а человеческий путь не создаёт
непроверенного межзонного ребра.

## 1. Изменение подписи цены во frontend

Последовательность пути:

1. `project/AGENTS.md`
2. `project/frontend/AGENTS.md`
3. `project/specs/analytics.md`
4. `project/specs/pricing.md`
5. `project/_ops/product-frames/pricing.md`

Первое решение: не показывать новое название тарифа без отдельного решения
владельца pricing frame. Для instruction-tree заменить чтение всех specs на
условный маршрут через `specs/pricing.md` к действующему frame.

Coverage: прочитаны весь действующий instruction path frontend-зоны, все
источники, которые требует текущий локальный файл, и конечный владелец
статуса. Gap: fixture не содержит конкретного frontend-файла или точной новой
подписи, поэтому конкретный diff UI не проверялся.

## 2. Изменение backend schema

Последовательность пути:

1. `project/AGENTS.md`
2. `project/backend/AGENTS.md`

Первое решение: до изменения `schema/**` выполнить `make schema-check`;
instruction-файл не менять.

Coverage: прочитан весь действующий instruction path backend-зоны. Gap:
fixture не содержит schema-файла, Makefile или вывода `make schema-check`,
поэтому выполнимость команды и результат конкретного schema-изменения остаются
непроверенными.

## 3. Человек редактирует onboarding-раздел README

Последовательность пути:

1. `project/README.md`

`project/AGENTS.md` был открыт в общей подготовке, но не входит в active set
этого пути: его цель явно адресована агентам, а субъект пути — человек.

Первое решение: не добавлять и не менять agent-facing instruction ради этого
пути; человек редактирует канонический onboarding-раздел напрямую.

Coverage: прочитан существующий onboarding-раздел README и проверена явная
agent-only область общего instruction-файла. Gap: запрос не задаёт содержание
человеческой правки, поэтому новый текст onboarding неизвестен и не
предлагается.
