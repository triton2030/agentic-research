---
description: "Launch one isolated Codex role or the native three plus Claude Premortem."
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

Одновременно запусти `ladder`, `solvent`, `prospector` через `spawn_agent` с
`fork_turns: "none"` и вызови один Claude Premortem по `$1claude-mcp`. Зоны —
вверх к цели, вниз под допущения, наружу к прецедентам, вперёд к
success-caused harm. У каждого native brief свой главный evidence path; два
briefs, осмысленные в чужих ролях, означают, что зоны не выведены.

Claude получает самодостаточный decision packet без гипотезы провала:

```text
Сегодня {date}; прошло {horizon}. Решение {decision} выполнено отлично — ровно
так, как задумано, — и именно успех привёл к неприемлемому вреду для {goal}.
Дай одну цепочку success → mechanism → harm; один ранний наблюдаемый signal и
где проверить его сегодня; state today с адресом; guardrail, сохраняющий
успех, и его цену. Плохое исполнение не подходит. Первая строка:
fatal_signal_present · signal_watchable · story_unfalsifiable.
```

Вызов обязан вернуть `resolved_model` другой семьи и terminal result.
`story_unfalsifiable` terminal, но не finding. Bridge/профиль недоступен —
точный blocker; своей историей провала чужую не подменяй.

## Named mode

Роль уже названа пользователем или trigger-ом; не добавляй панель. Запусти
один named `agent_type` с `fork_turns: "none"`.

- Critic получает общий brief и возвращает свой native verdict.
- `auditor`: `claimed done · atomic acceptance conditions · raw checks · known evidence/gaps · read-only boundary`; не подсказывай pass/fail.
- `md-scout`: `corpus · retrieval question · scope/exclusions · dependent decision · facts/gaps`; он возвращает evidence packet, не critic verdict.

Роль недоступна — верни точный blocker и остановись, не подменяя профиль.
