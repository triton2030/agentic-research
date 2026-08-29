---
description: "Launch the four isolated Claude panel lenses from one neutral decision packet."
---

# Panel Launch

Вход: decision anchor. Выход: terminal reports `ladder`, `solvent`,
`prospector`, `premortem`.

## Пакет каждой линзы

```text
Текущий маршрут/решение: {source-bound состояние без rationale main}.
Вопрос на столе: {что взвешиваем}.
Что изменит ответ: {следующий decision}.
Конечный результат: {owner goal или выведенный профессиональный outcome}.
Main уже читал: {paths; только список}.
Зона линзы: {другие главные sources, где проявится её falsifier}.
Факты: {source-bound или none}. Gaps: {material unknown}.
Границы: in — {scope}; out — {scope}; side effects — read-only.
Кругов пройдено: {только число, без маршрута и результатов}.
```

Не включай rationale main, его diagnosis, подозреваемую причину, желаемый
verdict или пересказ метода роли.

Запусти новые ordinary non-fork `Agent` streams четырёх named profiles.

Параллельный запуск предпочтителен; при нехватке capacity используй bounded
waves и сохрани уже полученные reports.

Каждая линза до вывода читает raw sources своей зоны, а не делает главным
входом файлы из `Main уже читал`.

Взаимозаменяемые briefs проваливают swap-test; исправь zones до запуска.

Не переходи к synthesis без четырёх terminal reports.
