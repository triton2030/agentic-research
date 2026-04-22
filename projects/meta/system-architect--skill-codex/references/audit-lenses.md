# Audit Lenses

Открывай этот файл, когда core workflow недостаточно и нужен более глубокий structural audit.

## Обязательные Линзы

- `Telos clarity`
  Где Goal или активный Stage слишком расплывчаты, чтобы на них строить durable architecture.

- `Capability reality`
  Какие hooks, validators, skills, plugins, tool constraints и owner surfaces реально существуют, а какие только упомянуты в текстах.

- `Force surface`
  Какие силы уже давят на систему и почему их нельзя оставлять в эпилоге после выбранного решения.

- `Weakest default path`
  Куда модель попадёт по пути наименьшего сопротивления в текущем устройстве.

- `Failure-class clustering`
  Какие seemingly разные симптомы на самом деле принадлежат одному классу сбоев.

- `Leverage over patch-count`
  Какая одна правка убирает несколько failure classes, и где система сейчас тянет тебя в bundle из мелких patch'ей.

- `Deletion candidates`
  Что можно удалить, не создавать или слить, чтобы default path стал проще и прочнее.

- `Folder justification and negative lists`
  Что каждая затронутая папка производит, какой Stage или preference её оправдывает и что туда не должно попадать.

## Trace Lens

Если текущий чат уже даёт signal:

- смотри на shortcut path, а не только на финальный ответ;
- отмечай, где модель пропустила upstream или capability reality;
- отделяй разовый промах от failure class;
- используй trace как evidence для leverage choice, а не просто как повод переписать один ответ.
