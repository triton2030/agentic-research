---
description: "Launch one user-named Codex critic, auditor or md-scout without a panel."
---

# Named Launch

Вход: пользователь явно назвал специализированную роль. Выход: один terminal
native product без панели.

Общий пакет передаёт current decision/state как source-bound факт, но не
rationale main, diagnosis, подозреваемую причину или желаемый verdict.

```text
Решение: {объект judgment · что изменит ответ · конечный результат}.
Professional question: {нейтральный вопрос выбранной роли}.
Evidence zone: {raw paths}. Факты: {source-bound или none}. Gaps: {unknown}.
Границы: in — {scope}; out — {scope}; side effects — read-only.
```

- Critic получает общий пакет и возвращает native verdict.
- `auditor` получает `claimed done · atomic acceptance conditions · raw checks · known evidence/gaps`; brief не подсказывает pass/fail.
- `md-scout` получает `corpus · retrieval question · scope/exclusions · dependent decision · facts/gaps`; он возвращает coverage/gaps packet, не critic verdict.

Запусти один named `agent_type` с `fork_turns: "none"`.

Роль недоступна — верни точный blocker и остановись, не подменяя профиль.
