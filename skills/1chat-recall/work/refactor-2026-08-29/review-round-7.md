# Review round 7 — локальные цели references

Дата: 2026-08-29.

## Решение владельца

Reference-файл с самостоятельной функцией может иметь собственную русскую
`Цель` и при необходимости `Уникальный контекст`. Они должны вести чистого
агента, чтобы выводимые инструкции не перечислялись повторно; exact interfaces,
safety/authority, критичный порядок, runtime seams и falsifying acceptance
остаются явными —
`_ops/chat-recall/2026-08-29-163434-codex-01a04d4a.md:21-22`.

## Что перенесено в intent

- Capture получил `Цель`: правильная тема и keyword-like metadata делают
  дословную запись будущим проверяемым адресом. Отдельный `Уникальный контекст`
  не нужен: модель записи уже находится в body и буквальном протоколе owner-а.
- Retrieval получил `Цель` и `Уникальный контекст`: candidates и metadata не
  являются ответом; результат — применимая позиция либо `abstain`, после чего
  продолжается исходная работа.
- Recovery получил `Цель` и `Уникальный контекст`: продолжает тот же claim;
  пустая выдача не доказывает отсутствие позиции; новый запрос оправдан только
  изменением candidate set.
- Restoring получил `Цель` и `Уникальный контекст`: переносит смысл в
  существующего semantic owner-а, не создаёт summary/profile и не превращает
  синтез агента в слова владельца.
- Repair получил `Цель` и `Уникальный контекст`: source-bound reconstruction,
  owner evidence как asset, ограниченный scope и terminal
  `capture-needed` → body-router → Capture.
- `validating-the-corpus.md` остался малым служебным reference из трёх шагов;
  декоративная цель не добавлена.

Удалены только повторы этих моделей: объяснение цены плохой темы, повтор
candidate-not-answer, повтор empty-recovery boundary, отдельные запреты
summary/profile и transcript import. Фальсификатор не сработал.

## Hard lines, которые остались

- Capture: полный read `topics.md` до записи, semantic comparison каждой
  границы, exact helper/schema, timestamps, `supersedes`/`contested`, JSON и
  адресная квитанция.
- Retrieval/Recovery: bounded routes, `truncated`, literal holder/record read,
  chronology, `--since`, применимые live owners, `recovery-needed`, terminal
  position либо `abstain` с gaps.
- Restoring: завершённый Retrieval как вход, существующий тип owner-а, видимый
  конфликт, no-owner gap и отчёт изменённых owners.
- Repair: admission через router/цель, project/session scope, порядок
  provenance, runtime-specific transcript CLI, sentinels, source timestamp,
  полный read тем, keyword metadata, backup/mutation boundary и integrity
  proof. `missing session-context` явно завершает Repair квитанцией; следующий
  Capture выбирает только body-router.

## Независимые проверки

- Первый буквальный pass нашёл одну двусмысленность: «передача в Capture» могла
  означать direct reference-chain. Исправлено на exact terminal receipt и
  body-router. Повтор 2: findings none.
- Trajectory pass 1 и 2: findings none. Эталон удержан:
  Capture → receipt → исходная работа; Retrieval/Recovery → position|abstain →
  исходная работа; Repair → integrity receipt либо `capture-needed` →
  body-router → Capture.
- Clean cases: Capture, Retrieval, Recovery, Repair-chain и Restoring — PASS в
  обоих runtime. В Repair одновременно открыт ровно один reference.
- Trigger-only clean probe установленной версии: use — «Запомни это правило
  для следующих решений»; skip — «Да, продолжай выполнять текущую команду»;
  near-miss → `chronicle` — «Найди ошибку, которую я видел на экране».

Консервативный atomic active-set (body + один reference), одинаковый для обоих
runtime: Capture ≥48; Retrieval ≥47; Recovery ≥59; Restoring ≥28; Repair ≥68;
validation ≥21. Он остаётся честным остатком, а не release blocker: clean-run
не показал пропущенной механики, один-reference topology сохранилась, а
микродробление увеличило бы переключения active context.

## Structural, functional и install evidence

- `quick_validate.py`: tracked и installed Codex/Claude — valid.
- Все ссылки из обоих `SKILL.md` существуют; `git diff --check` — clean.
- Suites после финальной seam-правки: Codex `101 passed, 12 subtests passed`;
  Claude `100 passed, 12 subtests passed`.
- Installed Retrieval на clean fixture: `matched=1`, `returned=1`,
  `truncated=false`, `retrieval=hybrid`, exact address
  `2026-08-29-183000-codex-33333333.md:15`.
- Repair fixture strict validator: `OK: 1 записей без diagnostics`; инструкция
  даёт exact terminal `capture-needed · <address> · missing session-context`.
- Claude live — symlink на tracked owner
  `skills/claude/1chat-recall`. Codex live синхронизирован из tracked owner без
  удаления cache-файлов.
- Functional manifest исключает только `.pytest_cache`, `.ruff_cache`,
  `__pycache__`, `*.pyc` и `.DS_Store`. Byte parity:
  - Codex tracked/installed:
    `cc2a6dad0f079bbe5d62bbc21de0d6253a7472b13f4cf2be5c9adf96b5f3f20e`;
  - Claude tracked/installed:
    `38bcde1535573082de1c91d9a0f0ea3b8cb3527af1dcd7c3912d028a0db78847`.

## Остаток

Число атомарных обязанностей высоко. Следующий refactor разрешён только по
наблюдаемому clean-agent сбою конкретного режима; сам счётчик не доказывает ни
потерю функции, ни необходимость нового reference-chain.

## Semantic edge review

`md-tools 0.7.0` нашёл у изменённого shared Product Frame три body-link
держателя и ни одного `depends-on`; у `cut.md` и этого review держателей нет.
Все три связи верны и дельтой локальных целей не затронуты:

- artifact 2026-08-13 ссылается на разрешённый model/cache bootstrap и правило
  «scores только направляют чтение»; слабую версию «Frame лишь упоминает эти
  свойства» отвергают явные строки `Допустимы...` и tie-breaker 2;
- artifact 2026-08-20 ссылается на применимую позицию, chronology, provenance и
  `abstain`; слабую версию «это исследовательская тема, не acceptance» отвергают
  `Цель` и `Acceptance retrieval`;
- artifact 2026-08-24 ссылается на запрет второго summary-store; слабую версию
  «Frame лишь предпочитает один слой» отвергает явное `Не вводить второй
  truth-store`.

Semantic edge review status for changed 1chat-recall history/frame: 3 связи
верны, 0 затронуто, 0 не прочитано, веток для переписывания нет.
