# Предложение

## `project/AGENTS.md`

`no-change`

Наблюдаемое основание: общий файл уже задаёт цель найти применимую
каноническую правду до решения, запрещает загружать несвязанные зоны и
маршрутизирует к ближайшему `AGENTS.md`.

## `project/frontend/AGENTS.md`

```md
# Frontend

Перед решением по price-facing UI следуй маршруту `../specs/pricing.md` к
указанному там действующему pricing frame.
```

Это заменяет широкий маршрут «прочитай все specs»: `specs/analytics.md` прямо
говорит, что не применим к подписи цены, а `specs/pricing.md` адресует
канонический действующий статус.

## `project/backend/AGENTS.md`

`no-change`

Наблюдаемое основание: для изменения `schema/**` уже задана локальная точная
hard line — выполнить `make schema-check` до изменения.

Новые instruction-файлы не предлагаются. `README.md`, `specs/**` и
`_ops/product-frames/pricing.md` остаются каноническими документами без
изменений.
