# Simplicity receipt — `1context-refactor`

## Цель

Оправдать каждую оставшуюся runtime-сложность конкретным вредом при удалении.

| Оставлено | Counterfactual harm без него |
| --- | --- |
| Session-wide analysis | Агент назначает причиной последний эпизод и теряет общий повтор. |
| Любой контекст, доступный до ошибки | Агент сужает поиск причины до последнего source и пропускает другие загруженные слои. |
| Pre-error evidence + alternative + counterfactual | Узнаваемый симптом превращается в ложный causal repair. |
| Independent route/finding gates | Causal unknown снова теряет доказанный оплаченный опыт. |
| Causal proof для advice/repair | Пользователь получает недоказанный совет, а source — правку не того механизма. |
| Authority + replay для source repair | Automatic trigger расширяет write scope и выдаёт текстовую возможность за эффект. |

Удалено или поглощено: все семь прежних runtime references; промежуточные
trace/test/preservation/repair и analysis/actions splits; refactor/coherence/
simplify/audit catalog; causal-card schemas; comparator catalog; обязательный
комплект outputs и runtime-каталог типовых ошибок. Exact candidate — один self-contained prompt: оба коротких
режима всегда применялись последовательно, поэтому отдельные файлы не меняли
решение и лишь добавляли stop-risk.
