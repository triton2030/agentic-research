# System Building Principles

Открывай этот файл, когда вопрос касается не только текста инструкций, а формы ИИ-системы: runtime layer, tools, memory, approvals, guardrails, eval и ownership.

## Осевой Принцип

Поведение системы — свойство структуры. Поэтому архитектор должен идти не от красивого ответа, а от:

`telos -> as-is reality -> forces -> failure classes -> leverage -> minimize`

## Принципы

- `As-is before design`
  Сначала карта реальных capabilities на текущей машине. Потом проектирование.

- `Forces are input, not epilogue`
  Давление будущего должно ограничивать выбор заранее, а не объяснять уже выбранный фикс.

- `Leverage beats patch bundles`
  Сильная архитектурная правка убирает класс сбоев, а не один симптом.

- `Minimize pass обязателен`
  Архитектура улучшается не только добавлением, но и удалением.

- `Runtime layer сильнее текста`
  Для опасных и repeatable сбоев сильнее validators, approvals, tool policy и sandbox, чем инструкция.

- `One owner per rule`
  Правило, размазанное по `_ops/`, `AGENTS.md`, skill и hook, уже начинает дрейфовать.

- `Observable > self-report`
  Любое важное правило должно иметь наблюдаемый сигнал, иначе оно не проходит проверку.

- `Sunset or archaeology`
  Если не знаешь, как поймёшь, что правило устарело, ты уже строишь археологию.

- `Questions only by EVPI`
  Вопрос оправдан только если меняет layer, owner или add-vs-remove решение.

## Частые Симптомы

- `Модель плавает между файлами`
  Частая причина: слабый owner graph и плохой as-is map.

- `Модель изобретает новый слой`
  Частая причина: capability reality не была проверена до prescriptions.

- `Правил становится больше, а системы — меньше`
  Частая причина: нет minimize pass и leverage analysis.

- `Архитектура выглядит умно, но не переживёт давление`
  Частая причина: forces оказались в epilogue вместо design input.
