# Проверки 1instruction-authoring v4

## Первый candidate

- `qv-skill`: pass; `plugin-eval`: 100/100, но это только structural/static
  evidence.
- Literal reviewer: fail — составные предикаты скрыли фактическую перегрузку,
  references запускали друг друга, часть прежней функции не имела producer-а.
- Trajectory reviewer: fail — обязательная цепочка превратила thin router в
  ритуал; зонному разведчику не хватало входа.
- Clean holdout «science status → все knowledge-файлы»: полезно вернул
  `stop` и не изменил root, но насчитал минимум 21 line-level и 68
  atomic-with-context смыслов; causal probe был недоступен.

## Принятые решения

- `next` удалён; условия стадий принадлежат только главному телу.
- References получили локальные «Уникальный контекст» и «Цель», русский body и
  короткие English trigger-only descriptions.
- Вход зонного разведчика сделан полным.
- Производители цели каждого файла, `Нерушимо:`, папки-склада, root-router и
  matched-tree probe восстановлены.
- Установка следует текущей authority без повторного approval.

## Повторный gate

- Final literal: PASS после исправления stop и causal gate; 11 файлов, 9
  внутренних ссылок, `qv-skill` pass. Reviewer раскрыл contamination одним
  прежним finding, поэтому его verdict используется как structural
  corroboration, не как clean behavioral evidence.
- Final trajectory: PASS. Допустимый путь:
  `intent → exact candidate → positive budget → positive causal delta без
  вреда → exact authority → owner → projections → parity`; любой неизвестный
  или отрицательный verdict сохраняет адреса.
- Clean controlled matched pair на одном evidence packet:
  baseline предложил создать `science/AGENTS.md` и `knowledge/AGENTS.md`
  без claim-level dependency graph; candidate вернул no-change, сохранил
  historical snapshots и назвал недостающие доказательства.
- `qv-skill`: pass на owner и четырёх runtime projections.
- `plugin-eval`: 100/100 на shared portable owner.
- Exact candidate ↔ shared owner ↔ Claude/Codex tracked ↔ installed:
  byte parity pass; sync check pass; internal links pass; `git diff --check`
  pass.
- Стабильный SHA-256 манифеста 11 candidate-файлов:
  `296a0b5677ec3fc24a625b0614ae5d6fd47b36b13bfbbd375b6543f3b75aec33`.

## Semantic edge review

Знаменатель: восемь ссылок `SKILL.md → references/*`, одна ссылка
`zones.md → agents/zone-scout.md` и четыре неисторических holder-а
`skills/shared/README.md`: `INDEX.md`, root `README.md`,
`skills/claude/README.md`, `skills/codex/README.md`. Tracked projections
исключены как byte-identical generated surfaces; два `_workspace` output-а
исключены и не прочитаны.

- Внутренние связи — «верна, новая, затронута и закрыта». Слабая версия:
  target лишь упоминает тему стадии. Её отвергают локальные «Цель», явный вход
  и адресуемый выход каждого target-а; условие router-а совпадает с этой
  работой. `zones → zone-scout` отдельно совпадает по полному зонному входу и
  требованию вернуть рёбра, а не instruction text.
- Четыре registry-holder-а — «верна, не затронута». Слабая версия:
  `skills/shared/README.md` лишь упоминает пакеты. Её отвергают разделы
  «Живые Owners» и «Синхронизация», которые действительно владеют выбором
  owner-а и projection flow. Изменение состава одного пакета не делает
  holder-фразы ложными.

Финальный claim: `semantic edge review status for shared
1instruction-authoring owner + registry holders` — 9 внутренних связей верны
и закрыты новой формулировкой; 4 внешних holder-а верны и не затронуты;
непрочитанный остаток внутри scope отсутствует.
