# Clean run — simple soft-delete lifecycle

## Fixture и исходное состояние

- Injected skill: `/Users/triton/Documents/GitHub/agentic-research/skills/1readable-code/recheck-2026-08-30/candidate/SKILL.md`.
- SHA-256, вычисленный до чтения: `6aa4ec3785d3c57d2cec142c92e4541dc52e114225661f9c5ffee7382e9496c7`.
- Ожидаемый SHA совпал с фактическим.
- Temp fixture: `/tmp/readable-code-simple.cJPujj` (на macOS разрешается в `/private/tmp/readable-code-simple.cJPujj`).
- Baseline: пакет `notes` экспортировал `Note`, `InMemoryNoteRepository` и `NoteService`; `NoteService.delete(note_id)` делегировал в repository, где `_notes.pop(note_id, None)` физически удалял запись. Два baseline-теста проверяли public get/list и физическое удаление.
- Baseline-команда: `python3 -m unittest discover -s tests -v` из temp fixture.
- Baseline-результат: `Ran 2 tests ... OK`.

## Фактическая траектория

`default → first changed decision → routes/subagents → edits → verification → closure`

1. **Default.** Я собирался добавить `deleted_at` к `Note`, оставить orchestration в `NoteService`, дать repository default-фильтрацию и отдельный физический purge.
2. **Первое решение, изменённое injected skill.** До фиксации новых service/repository-контрактов я остановился и маршрутизировал contract choice через `1codebase-design`, вместо немедленного добавления методов и флагов.
3. **Routes.** `1codebase-design` потребовал простой comparator, caller knowledge, locality и falsifier. Поскольку lifecycle является бизнес-инвариантом, его собственная инструкция маршрутизировала `1domain-modeling`. Репозиторное правило до нового кода маршрутизировало проверку prior art через `firecrawl-developer-index`: index подтвердил разделение logical delete и physical purge, а exact RCommon source подтвердил default filtering и отдельный unscoped lookup для restore.
4. **Subagents.** Вызовов subagent: **0**. После собственного суждения не осталось материальной стратегической неопределённости, и внешний взгляд не был прямо запрошен. Поэтому fresh view ничего не говорил; нечего было использовать или игнорировать.
5. **Edits.** `Note` получил `deleted_at` и идемпотентные transitions `delete`, `restore`, `was_deleted_before`. Repository теперь скрывает deleted в `get/list`, предоставляет отдельный `get_deleted` для restore и физически удаляет только в `purge_deleted`. `NoteService.delete(note_id)` сохранил публичную сигнатуру; добавлены `restore(note_id)` и `purge_deleted(before)`. Legal hold и actor audit не реализованы.
6. **Closure.** Falsifier не сработал: focused-тестам не пришлось обходить владельца lifecycle; restore читает deleted отдельным путём; поиск нашёл единственный hard-delete statement внутри purge.

## Design verdict

- Concrete pressure: сохранить caller-visible `delete(note_id)`, сменив его семантику с hard delete на обратимый lifecycle, и не дать normal reads случайно раскрыть deleted.
- Простейшая альтернатива без нового interface — добавить `include_deleted` к обычным `get/list`. Она увеличивает обязательное знание всех callers и делает escape hatch частью normal read surface, поэтому выбран отдельный `get_deleted`, используемый только restore-path.
- Новая абстракция или interface не добавлялись. Сохранены существующие `Note`, repository и service.
- Семантический владелец состояния и переходов — `Note`; владелец visibility и физического хранения — repository; пользовательские операции — service.
- Cutoff строгий: запись purged только когда `deleted_at < before`; равенство cutoff запись сохраняет.

## Проверка

Выполнены команды:

```text
python3 -m unittest discover -s tests -v
python3 -m compileall -q notes tests
python3 - <<'PY'
import inspect
from notes import NoteService
print(inspect.signature(NoteService.delete))
PY
rg -n "del self\._notes|\.pop\(" notes tests
```

Фактический результат:

- `Ran 6 tests in 0.009s — OK`.
- Compile check завершился с exit code 0.
- Сигнатура: `(self, note_id: str) -> None`.
- Поиск hard-delete: единственное совпадение `notes/__init__.py:51: del self._notes[note_id]`, внутри `purge_deleted`.
- Финальные SHA fixture-файлов: `notes/__init__.py` — `a33d7b4d3efd91bb4893ff0884417293b9f75e15096b248c933535c9a6b58d0c`; `tests/test_notes.py` — `8a4377aedd0345ac2e55c9eec1baab76712dc3055b6cc8d45d5f616bb80444ff`.

Помимо текущего happy path проверены:

- default `get/list` скрывают, но не удаляют soft-deleted note;
- повторный delete не сдвигает исходный `deleted_at`;
- повторный restore безопасен;
- delete/restore неизвестного id безопасны;
- purge на точной границе ничего не удаляет;
- purge после границы физически удаляет deleted note;
- тот же purge не затрагивает live-note;
- public `delete(note_id)` сохранил точную форму;
- иной физический delete-path в package/tests не найден.

## Локальность следующих изменений

- **Legal hold.** Не реализован. Самая локальная следующая правка — факт hold на `Note` и его учёт в принадлежащем `Note` purge-eligibility decision (`was_deleted_before` либо его более точное будущее имя). `NoteService` и normal read contracts менять не требуется; repository продолжит делегировать eligibility entity. Проверка сосредоточится на eligibility и purge negative path.
- **Actor audit.** Не реализован. Существующие transitions уже собраны в `Note`, поэтому audit metadata и запись actor принадлежат им; источник actor является отдельным будущим contract choice на service boundary. Это потребует правки `Note` и явного caller/service seam, но не repository filtering/purge mechanics. Текущая задача не даёт оснований заранее выбирать explicit argument против request context, поэтому такой контракт не выдуман.

## Отрицательная ветка: тривиальный rename

Для локального rename вроде `note_ids` → `purge_ids`, который не меняет public contract, seam, инвариант или test surface и не оставляет стратегической неопределённости, injected skill дал бы только короткую проверку влияния на будущую систему. `1codebase-design` и fresh subagent не вызывались бы. Сам rename не выполнялся, потому что он не требовался задачей.

## Candidate goals/context и расхождения

- До программирования были рассмотрены текущий lifecycle и будущие legal hold/actor audit.
- Ответственность разделена по одному ясному владельцу без новой speculative abstraction.
- Церемония осталась пропорциональной: contract route был выполнен, fresh subagent не вызван при отсутствии материальной неопределённости.
- Расхождений с целями или контекстом candidate в этом run не обнаружено.
- Непроверенное ограничение: fixture однопоточный и in-memory; concurrency, persistence failures и timezone validation не заявлены задачей и не проверялись.

## Аудит удалённых постоянных stages

**Наблюдаемый ответ для этого run: полезная функция не потерялась.** Функцию проверки альтернативы дал обязательный `1codebase-design`: сравнивались normal-read flags и отдельный deleted lookup. Функцию оспаривания дал claim-specific falsifier, после которого были добавлены boundary и live-note negative checks. Отдельная постоянная стадия не понадобилась, потому что после comparator не осталось равностоимой материальной ставки.

Это утверждение ограничено наблюдаемыми фактами этого запуска. Старый skill, history, reviews, другие receipts и control-run не читались, поэтому общий причинный вывод о всех задачах из этого одного run сделать нельзя.

## Verdict

**PASS для заявленного simple candidate:** lifecycle реализован минимально, тесты и структурные проверки проходят, сигнатура сохранена, subagent condition применён отрицательно и объяснимо.
