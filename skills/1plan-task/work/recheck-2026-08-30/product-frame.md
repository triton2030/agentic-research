# Product Frame — 1plan-task candidate

## Цель

Одна approved task становится автономным prompt одного ответственного агента.
Файл удерживает цель и load-bearing surprise-context, переживает обычное
continuation/handoff и останавливается при semantic change.

## Приёмка

- задача не дублирует соседнюю цель и исполнима в актуальной карте;
- один файл объясняет результат, смысл, boundary, stop и whole-result proof;
- названы только релевантные source addresses и немногие критичные строки;
- ориентир `20` улучшает упаковку, но не режет цель механически;
- semantic change возвращается в `1planning`, epic truth — в `1plan-map`;
- closure требует proof целого, а не только локально законченных шагов.

## Не-цель

Скилл не допускает задачу, не меняет эпик и не задаёт глобальную task schema.
