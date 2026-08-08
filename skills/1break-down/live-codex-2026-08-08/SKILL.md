---
name: 1break-down
description: >
  Use when a chosen approach is too large to execute directly and a full plan
  would hide dependencies, unknowns, or the next proof. Convert it into the
  nearest verifiable execution frontier without designing the whole task tree.
---

# Разбивка До Проверяемого Слоя Исполнения

## Зачем Этот Скилл Нужен

Когда путь уже выбран, тяжёлая работа провоцирует правдоподобный shortcut:
перечислить всю дорогу до финала. Полное дерево выглядит полезным, но после
первого ещё не полученного результата его нижние уровни уже опираются на
догадки. Наблюдаемый tell — гладкие будущие фазы с недоступными входами либо
proof, прохождение которого не меняет следующий ход.

Недостающий control act — вовремя сжать дерево у первого material evidence
point. Поэтому controller намеренно сводится к одному вопросу:

> Какой ближайший наблюдаемый результат изменит следующий ход, и какие блоки
> можно начать сейчас и действительно нужно завершить до него?

**Execution frontier** — минимальный ответ на этот вопрос: один material proof
и ready-блоки, чьи выходы в него сходятся. Это не `decision frontier` из
`$1planning` и не полный milestone plan.

## Вход И Authority

- Выбранный подход — вход скилла. Если основная развилка ещё открыта, верни ход
  owner-у подхода; декомпозиция не выбирает путь и не пересобирает цель.
- **Неизвестное** внутри выбранного пути ещё не принято за истину и может стать
  probe или gate. **Premise** уже считается истинной и удерживает outcome,
  scope либо путь; вокруг material premise разбивку продолжать нельзя.
- Если разные трактовки самого объекта дают разные первые фронтиры, задай один
  вопрос и остановись; не выбирай домен по тематике репо.
- Скилл не пишет файлы. Durable state для нескольких context/write slices
  принадлежит `$1planning`.

## Causal Demonstration

> Выбран перенос webhook-обработки в отдельный worker. Default — расписать
> queue, retries, deploy, dashboard и rollout. Frontier proof: записанный
> webhook проходит через минимальный worker, а повторная доставка даёт
> idempotent result. Failure меняет retry/idempotency contract; success снимает
> неопределённость перед production design. Cut оставляет fixture, adapter и
> assertions. Просто добавить всем будущим фазам input/output/check —
> anti-example: форма выполнена, граница сжатия не появилась.

Тот же controller переносится вне кода: для clause library ближайшим proof
может быть reviewed semantic preservation на репрезентативных договорах, а не
зелёный OCR всех файлов. Меняется домен, но не decision structure.

## Material Premise

Передай найденную material premise в `$1assumption-audit`. Если skill
недоступен, верни точную premise, её нагрузку на путь и остановку. После
`proceed` продолжи исходную разбивку; после `pre-phase` разбивай только выбранную
пред-фазу; после `reframe` не продолжай старую ветку.

## Feedback И Reopen

Если frontier скрывает missing input, декоративный proof, chronology без
зависимостей или downstream после proof, читай только совпавший tell в
[`references/decomposition-failures.md`](references/decomposition-failures.md)
и примени один repair.

Новое evidence, которое меняет proof, constraints или путь, инвалидирует
frontier: собери его заново, а не сохраняй уже записанный downstream.

Behavioral hypothesis ограничена текущим `GPT-5.6` target set; наблюдение —
2026-08-04. Смена target model set либо matched no-skill runs, в которых
premature depth больше не проявляется, reopen-ят контракт: удаляй ставший
лишним механизм, а не сохраняй его как вечную теорию.

## Return Gate

Собери shortest useful frontier packet:

1. **Proof:** один observable result плюс
   `failure → изменённый ход` и
   `success → снятая downstream-неопределённость`. Пустые контрфактуалы
   означают декоративный proxy — выбери другой proof.
2. **Ready cut:** только обязательные зависимости proof, каждая в форме
   `доступный вход → выход → проверка`. Missing fact/tool/authority замени
   минимальным probe, decision gate или точным handoff.
3. **Stop:** одна строка, явно закрывающая frontier у proof.

Перед отправкой потребуй четыре ответа `да`:

- каждый ready-блок можно начать сейчас из названных входов;
- все выходы сходятся в один proof;
- failure или success proof меняет дальнейшую работу;
- ответ не содержит задач, рекомендаций или side work, не нужных до proof, даже
  под ярлыком «параллельно», «обратимо», «опционально» или «на будущее».

Любой ответ `нет` означает: packet ещё не готов. Исправь proof или cut. После
строки Stop не продолжай планирование; следующую глубину разрешает только
полученное evidence.
