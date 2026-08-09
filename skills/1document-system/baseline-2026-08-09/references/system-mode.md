# System Mode

Проектируй минимальную полезную documentation system сейчас и явный путь её
изменения позже. Не материализуй будущую taxonomy заранее.

## Общая Модель

```text
future scenarios
→ information obligations
→ owners and artifact types
→ lifecycle
→ metadata and dependencies
→ topology
→ minimum materialization
```

Сначала прогрессивно прочитай живой проект и построй provisional scenario map.
Короткий известный target читай напрямую; известную папку с множеством файлов
передай `1md-read` по route `map descriptions/headings → select → bounded
extract`; неизвестный semantic owner ищи через scoped `1md-search`.
Map/rank выбирает bodies, но не назначает authority. Затем задай только вопросы,
ответы на которые меняют owners, types, lifecycle или topology.

## Logical Zones

Прочитай [topology-contract.md](topology-contract.md) и используй:

- `canon/`: current truth-bearing knowledge и durable evidence;
- `_ops/`: control/change state, включая `_ops/documentation/`;
- `projections/`: views, которые всегда имеют canon lineage.

В существующем проекте сначала отобрази текущие homes на эти роли. Не создавай
параллельные zones и не переименовывай существующие автоматически.

## Greenfield

1. Зафиксируй boundary, readers, edit/retrieval scenarios и ближайшие решения.
2. Выведи только types, без которых сейчас остаётся самостоятельный information
   gap. Проверь их через [catalog.md](catalog.md) и назначь current home.
3. Если запрос разрешает реализацию, materialize `_ops/documentation/` и создай
   один содержательный artifact: `_ops/documentation/DOCS — Documentation
   System Map — <project>.md`. Другие zone/folder homes создавай только вместе с
   первым admitted current artifact; не создавай empty skeleton.
4. В map сохрани: boundary; zone contract; progressive retrieval paths;
   admitted type registry, default homes и токен-бюджеты admitted types
   (число на файл + исполняемая проверка); folder-axis policy; metadata profile
   с retrieval-label outcome по
   [metadata-contract.md](metadata-contract.md); current topology; future
   roadmap; open questions; stop conditions.
5. Future type запиши только в roadmap: scenario, information obligation,
   likely type/home и observable activation trigger. Не создавай folder,
   template или registry entry до admission.

## Refactor

Результат Refactor — target `DOCS — Documentation System Map — <project>.md`
с dispositions по файлам, а не переписанное дерево. Target model выводится из
будущих сценариев, не из желания нормализовать текущую taxonomy.

Target map достаточно полна, когда:

- охвачен весь documentation corpus, кроме content внутри `projections/` по
  умолчанию; canon, ops/workbench и ambiguous files различимы;
- для каждого файла названы current role, target owner/type и disposition:
  `keep`, `merge`, `split`, `projection`, `archive` или `unresolved`;
- mixed files имеют section-level dispositions и provenance;
- для каждого duplicate/conflicting изменяемого ответа названы occurrences,
  подтверждённый owner и authority evidence либо `owner unresolved`, а также
  уникальные claims/evidence/provenance, которые нельзя потерять, и результат
  остальных occurrences: local implication + pointer, merge или archive;
- similarity и качество текста используются как discovery signals, но не как
  authority verdict.

Остановись на mapping. Rewrite, move, delete и archive cutover принадлежат
отдельным принятым задачам; когда такая задача принята,
её исполнение ведёт [compaction-safety.md](compaction-safety.md) — mapping не
описывает, как удалять текст без тихих потерь.

## Admission Нового Type

Создай project-local candidate, только если он владеет самостоятельным
изменяемым ответом и имеет хотя бы один независимый seam: lifecycle, reader,
validation или owner. Различие scope само по себе не создаёт seam. Иначе
используй module существующего type либо projection.
Global catalog не меняй без отдельной явной просьбы.

## Closeout

Проверь: logical zones различимы; current types отделены от roadmap; пустая
taxonomy не создана; ops не стал current truth; projection имеет lineage и не
стала source; local owner-map остаётся router-ом, а не вторым product canon. Для
большого corpus подключай [delegation.md](delegation.md) только после
независимого split.

