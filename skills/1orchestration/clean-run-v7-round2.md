# Clean-run v7 — второй кандидат

Проверенная версия: manifest
`9e7fcd204f1d58f2fcdc5963782896a767140dbd916b3b59412bd2deeb517422`.
Чистый исполнитель не читал predecessor, history или reviews.

Реалистичный случай: один read-only субагент сравнивает цель `_ops/GOAL.md` с
Product Frame и возвращает адресованные совпадения/расхождения; root сохраняет
приёмку.

Фактическая траектория:

`orient → brief → rough estimates → direct-assignment → accept(rework)`.

- `AGENTS.md` открыл обязательный Principles-source. Ранние производные были
  инвалидированы и пересобраны с самой ранней затронутой стадии.
- Actor estimate: `13`, root next-decision estimate: `9`; оба уверенно
  manageable, поэтому полный `count → budget` не открывался.
- Способность read-only исполнителя достаточна; topology не создавалась,
  runtime lifecycle и приёмка остались у действующих владельцев.
- Return «Проверил оба файла: цели в целом согласуются» получил `rework`:
  отсутствовали адреса, логическая цепочка, классификация расхождений и
  no-change evidence.
- Зависимость осталась заблокированной; rework передал только недостающее
  evidence, не повторил доступные источники.

Use: назначение subagent. Skip: посильная root-only работа. Near-miss: разбить
короткую root-only работу на checklist без перегруза. Trigger — короткий
English trigger-only; тело и references — русские; `20` мягкий; шесть
самостоятельных references имеют локальные цели.
