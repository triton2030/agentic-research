# Event Vs Structure Conflation

## Observation

При моделировании lifecycle артефактов модель склонна применять **одинаковую closure shape** ко всем элементам иерархии без проверки их семантики. Конкретно: применила «папка-капсула с датой» одинаково к **task** (discrete event — закрылась в день X) и к **stage** (live structure — переписывается во времени через rename/split/merge/remove).

Pattern: **uniform symmetry as default modeling stance.** Когда есть иерархия (task ⊂ stage ⊂ roadmap), модель проектирует единую shape сверху вниз. Симметрия выглядит чисто и легко объясняется, но прячет онтологическое различие:

- **Event entity** — закрывается в момент времени. Date в имени = когда событие случилось. Task closure такой.
- **Structure entity** — существует во времени, меняет форму. У неё нет single closeout date, есть transitions. Stage такая.

Применить event-shape (capsule с датой) к structure entity = форсировать modeling, который не лежит на реальности.

## Counter

- 2026-05-20 [Claude Opus 4.7]: archive shape для `1planning` (Claude + Codex). Я предложил вариант B «папка-капсула с датой» одинаково для task И stage: `_ops/plans/_archive/YYYY-MM-DD-<stage-slug>/` со snapshot pre-split и pre-merge. User прервал: «стадии не архивируются но переписываются и иногда по разному». Перестроил на task-only capsule + stage-as-namespace (без даты) при transitions. Cost: один лишний турновый цикл + два rollback edit'а.

## Possible upgrade

Перед применением единой shape к иерархии — спросить про каждый уровень: **это event или structure?**

- Закрывается ли единичным актом в момент времени? → event, date применима.
- Существует ли во времени и меняет форму? → structure, namespace без даты.
- Имеет ли single owner / single deliverable? → event-leaning.
- Подвержена rename / split / merge transitions? → structure-leaning.

Применимо: archive design, lifecycle modeling, versioning schemes, naming conventions для иерархий, snapshot policy.

Симметрия в моделировании — failure mode, не достоинство. Когда все уровни иерархии «выглядят одинаково» в schema — стоит явно проверить, не приклеена ли event-shape к structure entity.

Релевантно: любое modeling работа где есть mixed-lifecycle hierarchy (project → stage → task → subtask, repo → branch → commit, document → section → paragraph, etc).
