# profit-forecast — аудируемый лист вероятности прибыльности MAVO

Детерминированный расчёт вероятности прибыльности из 9 звеньев `Ставка_MAVO`. Форма — **произведение вероятностей по группам** (AND-цепочка Ставки «все звенья должны быть правдой одновременно»), БЕЗ Monte Carlo: V/A/B не оцифрованы, строгость на них была бы ложной точностью. Приоры — `self_canon` owner-judgment до pre-pilot, широкие; каждая клетка видна руками.

## Файлы

- `nodes.csv` — 9 звеньев: `gate_role` (hard/soft/contributor/long_horizon), `group` (pilot/unit/scale), `status`, `source_strength`, `p_low/base/high`, `kill_criterion`, `lever_evidence`, `evidence_stage`, `source`.
- `configurations.json` — бизнес-конфигурации: решения, node overrides, defeaters.
- `forecast.py` — калькулятор: три числа + worst-link интервал + рычаги по группам + денежный слой + comparison двух конфигураций.
- `tests/test_forecast_engine.py` — characterization текущего baseline и первого radical recommendation probe.

## Запуск

```bash
python3 forecast.py
python3 forecast.py --compare dog_owners_without_print_studios studios_current
python3 forecast.py --compare dog_owners_without_print_studios studios_current --json
python3 -m unittest discover tests
```

## Три числа (разные вопросы, не сумма)

- `Y_pilot` — докажет ли пилот жизнеспособный клин (спрос → платёж → печать → соло);
- `Y_unit` — unit-экономика положительна (дешёвый SKU + сходится);
- `Y_scale` — связка защищаема на масштабе.

## Правила честности

- Число подчинено статусу Ставки: kill-gate ведёт **прежде** скаляра.
- Наивное произведение = консервативный **пол**; положительная корреляция звеньев поднимает совместную вероятность выше. Ценность — в **сравнении** трёх чисел и в рычагах, не в абсолютной цифре.
- Рычаг считается **внутри группы** (pilot/unit/scale — разные вопросы; их рычаги не сравнимы между собой).
- Ширину доминирует **слабейшее звено** (worst-link), не среднее.
- Сузить интервал = **закрыть рычаг реальным замером**, не подкрутить приор.
- Приоры `self_canon` — черновые; уточняются reference-class base rates (Codex как дешёвый субагент) и pre-pilot.
- Рекомендация меняет **business decision configuration**, не прозу канона. Canon patch допустим только после owner gate: `owner_accepts_risk_before_canon_patch`.

## Первый probe рекомендации

`dog_owners_without_print_studios -> studios_current` доказывает минимальное поведение:

- dog-конфигурация убивает `Z2` / `Z3` / `Z6`, поэтому `Y_pilot` становится `0%`;
- studio-конфигурация возвращает baseline `Y_pilot ≈ 6%`;
- вывод имеет статус `model_recommendation`, а не обещание рынка.

## Отложено до after-pilot

Monte Carlo / Bayesian-сеть, Brier-калибровка (нужны разрешённые прогнозы пилота). Пока входов нет — это была бы ложная точность.
