---
description: "Launch one isolated named role or the four-lens Claude panel."
---

# Launch

Вход: decision anchor и выбранный mode. Выход: terminal native report каждого
обязательного профиля.

## Общий brief

```text
Решение: {вопрос на столе · что изменит ответ · конечный результат}.
Зона: {raw paths/срез, где falsifier этой роли проявится; кругов пройдено}.
Evidence: {source-bound facts или none}. Gaps: {существенное неизвестное}.
Границы: in — {scope}; out — {scope}; side effects — none/read-only.
```

Не включай гипотезу main, его маршрут, подозреваемое место, желаемый verdict
или пересказ метода роли. Brief самодостаточен; профиль читает названные raw
sources до своего первого вывода.

## Panel mode

Запусти одновременно новые ordinary non-fork `Agent`-потоки `ladder`,
`solvent`, `prospector`, `premortem`. Их зоны — вверх к цели, вниз под
допущения, наружу к прецедентам, вперёд к success-caused harm.

У каждого brief свой главный evidence path. Если два заполненных briefs
осмысленны в чужих ролях, зоны не выведены. Дождись terminal report всех
четырёх; Premortem сам владеет cross-family вызовом.

## Named mode

Роль уже названа пользователем или trigger-ом; не добавляй панель.

- Critic получает общий brief и возвращает свой native verdict.
- `auditor`: `claimed done · atomic acceptance conditions · raw checks · known evidence/gaps · read-only boundary`; не подсказывай pass/fail.
- `md-scout`: `corpus · retrieval question · scope/exclusions · dependent decision · facts/gaps`; он возвращает evidence packet, не critic verdict.

Роль недоступна — верни точный blocker и остановись, не подменяя профиль.
