---
description: "Claim-bound activation, adherence, completion and ablation evidence."
---

# Evidence

До прогона зафиксируй claim, bypass, acceptance/metric и cheapest comparator.
Для rewrite baseline — исходная версия; `no skill` не оправдывает механизм,
если меньший owner-delta уже работает.

## Три lane

1. **Activation:** грязные should/should-not/near-miss prompts против живых
   соседей; проверь description canvas и metadata shortening.
2. **Uptake/adherence:** на непоказанной задаче ищи другое решение,
   task-local compilation и действие по source/check. «Прочитал», процитировал
   или заполнил секции — не применение.
3. **Completion:** внешний verifier/acceptance artifact отличает outcome от
   proxy. Каждый applicable MUST имеет evidence либо `N/A`/`blocked`.

Claim «стало вероятнее» требует matched repeated runs: одинаковые resolved
model/settings/task; новая версия против baseline. Один success = возможность,
не uplift. 2–3 задачи покрывают ветви, но не дают статистического claim.

Меняй по одному semantic component: description, rationale, point-of-action
check, route или completion gate. Повтори набор и сохрани regression: это
ablation.

Не сообщай evaluator-у диагноз/ответ. Ceremony без иного choice/evidence удаляй.
Обобщай механизм; оставь unseen branch.

Отдельно проверь package, ссылки, live owner и installed projections: это
distribution, не cognition.

Отчёт: `claim | baseline | task/model/runs | delta | failures | status`.
Непокрытая lane остаётся gap. Target-model change, исчезновение failure trace
или отрицательная ablation reopen-ят skill.
