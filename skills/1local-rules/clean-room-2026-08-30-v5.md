# Clean-room reimplementation v5

Исполнитель получил только `intent-2026-08-30-v5.md` в сообщении и не читал
старый package или history.

Он применил Clean-room Reimplementation и Zero-based Design и вернул
self-contained runtime draft без references, стадий и отдельного approval
процесса.

## Семантический черновик исполнителя

Исполнитель оставил семь смысловых единиц:

1. Положительный trigger: один проект, `2*`, оба runtime.
2. Skip: global и single-runtime skill.
3. Разделение ответственности с `1skill-creation` и старшими инструкциями.
4. Только явно объявленные проектом owner и sync route.
5. Один project route для create, update и retire с приоритетом старших
   инструкций.
6. Инвариант «обе одинаковые проекции или ни одной».
7. Наблюдаемая проверка допустимого состояния.

## Counterfactual harm исполнителя

| Единица | Без неё разумный дефолт | Конкретный вред |
| --- | --- | --- |
| Trigger | Запустить обычное создание | Локальный package потеряет `2*` или dual-runtime scope |
| Skip | Принять любой local/global skill | Global либо Claude-only skill ошибочно станет dual-runtime `2*` |
| Разделение ответственности | Повторить весь creator flow | Runtime contract накопит review и approval бюрократию |
| Declared topology | Вывести owner из текущих файлов | Случайная projection станет вторым owner |
| Один project route | Править ближайшую projection | Update/retire разойдутся между средами |
| Terminal invariant | Принять одну рабочую projection | Claude и Codex получат разные состояния |
| Наблюдаемая проверка | Принять запись за завершение | Partial state будет объявлен готовым |

## Поглощено intent

Обычное проектирование, проверка и exact approval поглощены
`$1skill-creation` и старшими инструкциями.

Topology и sync mechanics поглощены явной декларацией проекта.

Create/update/retire сведены к одному проектному маршруту и двум допустимым
terminal states.

Review stages, manifest, отдельный approval flow, receipts, rollback и
drift-recovery не внесены.

## Фальсификатор

Если реальный project route регулярно оставляет одну проекцию без второй и
невозможно проверить terminal state, потребуется отдельный механизм
восстановления.

До наблюдения такого провала recovery-процедура не является частью runtime
skill.
