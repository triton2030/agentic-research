# Audit Lenses

Открывай этот файл, когда core workflow недостаточно и нужен более глубокий structural audit.

## Обязательные Линзы

- `Project reality clarity`
  Где сам проект, его цель или текущая траектория слишком расплывчаты, чтобы на них строить instruction layer.

- `AI job map clarity`
  Какие типы работы ИИ реально должен делать в проекте, а какие ты подставил по привычке.

- `Pressure surface`
  Какие силы уже давят на систему и почему их нельзя оставлять в эпилоге после выбранного решения.

- `Weakest default path`
  Куда модель попадёт по пути наименьшего сопротивления в текущем устройстве.

- `Failure-class clustering`
  Какие seemingly разные симптомы на самом деле принадлежат одному классу сбоев.

- `Control surface reality`
  Какие `AGENTS.md`, skills, hooks, validators, folder rules и approvals реально влияют на поведение, а какие только названы.

- `Leverage over patch-count`
  Какая одна правка убирает несколько failure classes, и где система сейчас тянет тебя в bundle из мелких patch'ей.

- `Deletion candidates`
  Что можно удалить, не создавать или слить, чтобы default path стал проще и прочнее.

- `Folder justification and negative lists`
  Что каждая затронутая папка производит, какой Stage или preference её оправдывает и что туда не должно попадать.

## Trace Lens

Если текущий чат уже даёт signal:

- смотри на shortcut path, а не только на финальный ответ;
- отмечай, где модель пропустила project reality, AI job map или control surface reality;
- отделяй разовый промах от failure class;
- используй trace как evidence для leverage choice, а не просто как повод переписать один ответ.
