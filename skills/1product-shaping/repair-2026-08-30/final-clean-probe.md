# Final clean probe — exact package c34fdcf

Read scope: только три файла
`skills/1product-shaping/candidate-repair-2026-08-31/**`. Записей не было.

## Proposed `weekly-review.principles.md`

```markdown
# Product Principles · weekly-review

## P-001 · Проверенная рекомендация важнее покрытия

Показываем клиенту проверенную рекомендацию, а low-confidence alert клиенту не
показываем. Это не решает технический threshold.

## P-002 · Ручная работа допустима во время проверки

Во время проверки платного спроса допустимы ручная analyst review и manual
prep; self-service и публичный dashboard не строим. Это не решает внутренний
tooling.
```

## Proposed `weekly-review.md`

```markdown
# Product Frame · weekly-review

## Цель

За 14 дней проверить платный спрос на еженедельный AI operations review для
ops lead агентства размером 20–100 человек, который получает findings до
планёрки в понедельник.

Приёмка: три оплаченных пилота в течение двух недель используют findings на
понедельничной планёрке.

Доказательство: invoices и записи встреч.

## Привязка к цели проекта

Служит цели проекта проверить платный спрос на еженедельный AI operations
review за 14 дней → из-за этой цели не строим публичный dashboard.

## Тайбрейкеры

- Когда покрытие конфликтует с проверенностью рекомендации, выбираем
  проверенную рекомендацию (`P-001`). Это не решает технический threshold.
- Когда low-confidence alert конфликтует с требованием показывать клиенту
  только проверенную рекомендацию, alert клиенту не показываем (`P-001`). Это
  не решает технический threshold.
- Когда автоматизация конфликтует со своевременной проверкой спроса, допустима
  ручная analyst review и manual prep (`P-002`). Это не решает внутренний
  tooling.
- Когда self-service или публичный dashboard конкурируют с проверкой платного
  спроса, их не строим (`P-002`). Это не решает внутренний tooling.

## Старшинство

`GOAL` старше этой пары. При конфликте `GOAL` побеждает, запись пары
останавливается, а изменение `GOAL` выполняется отдельно.

## Аппетит

- Срок: 14 дней.
- Бюджет на tools: до $500.
- Допустимая жертва: manual prep.
- Недопустимая жертва: пропустить понедельник.
- Пересмотр: при трёх paid pilots или если prep превышает 2 часа на клиента.
```

## Proposed `history.md` receipt

```markdown
## 2026-08-31 · weekly-review — proposed, not appended

- Затронутая пара: `weekly-review.md`, `weekly-review.principles.md`.
- Затронутые принципы: `P-001`, `P-002`.
- Причина: сформировать повторяющуюся продуктовую область для 14-дневной
  проверки платного спроса на weekly AI operations review.
- Источник GOAL: «за 14 дней проверить платный спрос на еженедельный AI
  operations review; ручная доставка допустима; публичный dashboard не
  строим».
- Источник owner truth: шесть подтверждённых фактов holdout-сценария.
- Прежний смысл: не установлен в разрешённом read scope.
- Новая полномочная граница: пара разрешает выбор в пользу проверенной
  рекомендации, сокрытия low-confidence alerts, ручной analyst review/manual
  prep и отказа от self-service/public dashboard; technical threshold и
  внутренний tooling не решает.
- Затронутые downstream-артефакты: не установлены в разрешённом read scope.
- Evidence точного одобрения всей версии: отсутствует.
- Статус: не имеет права на append до точного одобрения всей пары.
```

## Rejected unsupported claims

- `P-003 email delivery preferred` — отклонён.
- `P-004 weekly PDF` — отклонён.
- `P-005 invite teammates` — отклонён.
- Канал доставки, формат deliverable и доступ teammates не попали ни в одну
  половину пары.
- Прежний смысл и downstream-карта не выдуманы.

Terminal state: `AWAITING_EXACT_FULL_PAIR_APPROVAL`.
