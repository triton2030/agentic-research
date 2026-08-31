# Product Frame — `1context-refactor` — candidate 2026-08-30

## Цель

После повторяющихся ошибок, переделок или лишнего поиска агент восстанавливает
паттерны по всей доступной сессии, проверяет механизм влияния контекста и
сохраняет каждый доказанный post-factum результат у его владельца.

## Приёмка

- Вход происходит только после наблюдаемого повтора; будущие риски принадлежат
  `1instruction-authoring`.
- Session trace покрывает все доступные эпизоды и честно называет gaps.
- Причиной считается только pre-error контекст с activation evidence,
  strongest alternative и различающим counterfactual.
- Доказанная цена поиска независимо проходит gate `1index`, даже если causal
  verdict остаётся hypothesis или unknown.
- Наблюдаемая системная проблема независимо проходит gate `1findings` с
  честным causal status; blocker находкой не маскируется.
- Совет о словах пользователя и source repair требуют доказанного causal
  involvement; repair дополнительно требует write authority и replay.
- Неприменимые branches не фабрикуются.

## Не-цель

Скилл не прогнозирует будущие ошибки, не сливается с `1index`, не получает
универсальное право переписывать контекст и не хранит общие методы refactor,
coherence, simplification или audit вместо их semantic owners.

## Тайбрейкеры

1. Полная session trace сильнее удобного одиночного эпизода.
2. Pre-error source сильнее поздней находки.
3. Наблюдаемый mechanism сильнее узнаваемого паттерна.
4. Собственный evidence-gate результата сильнее общего causal gate.
5. Semantic owner сильнее удобной поверхности записи.

Owner evidence:
`_ops/chat-recall/2026-08-29-205016-codex-01a04e33.md:22-23,25-26`.

Статус: exact candidate; official owners, projections и live не меняются до
безусловного approval этих байтов.
