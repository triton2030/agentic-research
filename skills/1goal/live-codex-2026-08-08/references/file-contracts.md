# Контракты Файлов - `1goal`

## Карта Владения

- `_ops/GOAL.md` — единственный semantic owner долгоживущей цели репозитория.
- Root `README.md` — narrative context и on-ramp; `1goal` меняет только его
  goal-related смысл или pointer.
- Root `AGENTS.md` / `CLAUDE.md` — effective instruction layer. Она требует
  прямого чтения GOAL, но не становится владельцем его содержания.
- Product frames — выбранная форма одного продукта или крупной работы внутри
  цели.
- `_ops/plans/**` — порядок, status, evidence и lifecycle исполнения.

Pointer, summary и downstream constraint не являются вторым owner-ом, пока не
повторяют полный scope, anti-scope или decision thresholds GOAL.

## `_ops/GOAL.md`

Назначение: короткий repository charter, который fresh agent читает до
нетривиальной работы и использует для выбора между правдоподобными направлениями
на любом этапе проекта.

Предпочтительная компактная форма:

- **Purpose** — устойчивый эффект, ради которого существует вся папка, и для
  кого или чего он важен;
- **Durable scope** — классы вклада, совместимые с purpose при смене текущих
  продуктов и технологий;
- **Anti-scope** — привлекательные классы работы, которые репозиторий сознательно
  не оптимизирует;
- **Decision tests** — 2-4 типовые развилки, показывающие accept, reject или
  preference;
- **Evidence of alignment / drift** — наблюдаемое состояние системы решений и
  артефактов, а не список завершённых задач;
- **Reopen conditions** — какие новые знания делают верхний контракт
  сомнительным и требуют нового owner signoff.

Сохраняй уже установленный local dialect и headings, если их смысл позволяет
держать эти функции. Не устраивай migration ради названий. Если локальная форма
требует `Definition of done`, описывай устойчивое проверяемое состояние или
порог пересмотра, а не момент, когда «вечная» цель закончилась.

GOAL работает, когда:

- остаётся верен после мысленного удаления current plans и product frames;
- меняет verdict хотя бы в одной правдоподобной будущей развилке;
- позволяет заметить alignment или drift без устного контекста;
- остаётся коротким и не превращается в narrative, правила или task list.

GOAL дрейфует, когда в нём появляются:

- текущие продукты, features, этапы, roadmap или технологии как сама цель;
- status, tasks, commands, evidence log или closeout;
- инструкция вида «каждый X обязан Y», не выражающая стратегическую границу;
- vision без beneficiary/effect, anti-scope и решения, которое она меняет;
- локальный вывод product frame, автоматически повышенный до repo-wide truth.

## `README.md`

README объясняет cold reader-у, что это за репозиторий, почему он устроен так и
куда идти дальше. Он может дать короткую narrative-интерпретацию цели и ссылку
на `_ops/GOAL.md`, но не повторяет durable scope, anti-scope, decision tests или
reopen conditions.

Текущий контекст допустим как on-ramp, если явно не назван постоянной целью.
Status registry, task index, operational rules и полный GOAL-контракт живут у
своих owners.

## Direct-Read Projection

Fresh agent должен получить обязательный прямой маршрут к `_ops/GOAL.md` из
effective root instructions. Достаточны короткий imperative pointer и, если
нужно для routing, одна строка essence. Не вставляй туда полный пересказ цели.

При создании или semantic change GOAL:

1. проверь, что direct-read requirement реально действует для repository root;
2. синхронизируй существующую узкую projection;
3. если instruction mechanism отсутствует или требует структурной переработки,
   передай её owner-у instruction layer, не проектируй новую систему внутри
   `1goal`;
4. перечитай GOAL, README и projection напрямую и проверь, что semantic owner
   остался один.

## Semantic Edge

Ссылка из `SKILL.md` на этот файл выполняет `application/constraint` job: после
owner signoff reference задаёт точную форму записи и проекций, но не владеет
стратегическим интервью. Изменение этих контрактов делает link `affected` и
требует совместного перечитывания обеих сторон.

Graph/path green доказывает только разрешимость адреса. Semantic sync проверяй
по тому, одинаково ли GOAL, README и instruction projection направляют решение,
не создавая второго owner-а.
