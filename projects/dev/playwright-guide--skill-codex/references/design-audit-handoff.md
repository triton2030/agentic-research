# Design Audit Handoff

Использовать, когда browser-pass уже собрал visual evidence и дальше нужен разбор качества интерфейса.

## Куда Передавать Дальше

### `$screenshot-design`

Выбирать, если:

- основное evidence теперь статичный screenshot;
- вопрос именно визуальный;
- не нужно дальше трогать live page.

## Что Передавать

- какой экран или section проверяли
- какой breakpoint
- какой visual question решаем
- какой evidence уже собран
- где проходят границы уверенности

## Что Не Передавать

- лишние догадки о том, что пользователь "точно почувствует"
- выводы, которых нет в pixels
- необязательные коды, если review дальше идёт от изображения

## Хорошая Связка

1. `playwright-guide` выбирает browser path
2. `$playwright` или `$playwright-interactive` собирает evidence
3. review-skill делает визуальный вывод

Так layout evidence и visual judgment не смешиваются слишком рано.
