---
description: "Detailed Gate 0-1 operations for admitting one bounded IA question and confirming authority before operation comparison."
read-when: "Read first for every material 1ia-audit case; stop here when the question is not material or authority cannot be resolved."
---

# Admission And Authority

Этот файл владеет детальными операциями Gate 0–1. Основной `SKILL.md` владеет
порядком фаз и stop-условиями.

## Gate 0 — Допусти Bounded IA-Вопрос

1. Назови mode: `audit`, `design` или явно разрешённый `change`.
2. Раздели current surface и proposed change/question; отсутствие current form
   в greenfield не превращает candidate в baseline.
3. Ограничь surface точным document, section или container и назови, что
   намеренно остаётся вне verdict-а.
4. Запиши primary reader/agent и один observable action, ради которого существует
   форма.
5. Запиши mutable answer или obligation, который reader должен найти, применить
   либо изменить.
6. Проверь materiality: если форма не меняет information job, путь к mutable
   answer или update/validation surface, классифицируй вопрос как `not material`.
7. Выпиши material premises, уже принятые запросом или proposed shape за истину.
   Если отрицание premise меняет scope, owner или verdict, проверь её по body/
   usage evidence либо пометь `unknown`.

**Результат gate:** `mode + bounded current/proposed subjects + reader action +
mutable answer + materiality + premise status`. Нет material IA-вопроса —
остановись на `not material`; не изобретай redesign.

## Gate 1 — Зафиксируй Authority И Information Jobs

1. Назови candidate semantic owner mutable answer-а, не место, где текст
   случайно найден.
2. Прочитай live responsibility, normative contract или другой прямой body,
   который назначает эту authority.
3. Присвой status `confirmed` либо `unresolved`; polish, rank, filename и удобная
   новая форма owner-а не назначают.
4. Отдели semantic owner от current container, view, index и физического
   placement: это разные оси.
5. Назови, кто и при каком trigger-е обновляет answer, а также его lifecycle.
6. Назови check/validator и dependent view/consumer, если они действительно
   участвуют в одной операции.
7. Раздели primary job и secondary material. Secondary job остаётся внутри,
   только если обслуживает того же reader-а, lifecycle и validation.
8. Для предполагаемой seam проверь независимость сторон по reader, owner,
   lifecycle, edit trigger и check. Headings или темы без такой независимости
   seam не доказывают.
9. Если спорны information moves, section grammar или mixed functions, вернись
   к прямому route на `document-form-lens.md` из основного `SKILL.md` до trace
   design.

**Результат gate:** `confirmed|unresolved owner + owner evidence + primary/
secondary jobs + lifecycle + validation + seam independence`. Authority
unresolved → downstream verdict остаётся `unknown`, даже если shape выглядит
очевидной.
