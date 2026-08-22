---
kind: module-card
wave: "6d"
state: ready-for-draft
role: chronological-serial-wiki-writer
system-owner: root
batch-model: gpt-5.6-luna
batch-thinking: max
---

# Модуль — chronological batch-002

[parent: task.md](../task.md) · второй bounded probe после принятого batch-001
checkpoint · тот же visible Codex Luna thread, local project, без worktree]

## Outcome

Встроить следующие десять frozen holders в текущую Wiki как знание на boundary
batch-002. Сначала Luna возвращает полный evidence-mapped draft changeset; root
проверяет его; только затем Luna материализует ровно утверждённые bytes в
существующий Wiki tree. Batch проверяет настоящее `update/supersede`, но не
разрешает автоматически остальной corpus.

## Frozen input

Единственный manifest —
`experiments/openviking-chat-recall/artifacts/chronological-pilot/batch-002-input.json`.
Он фиксирует 10 holders, 20 records, 0 diagnostics, corpus commit, F2 digest,
prior Wiki tree/receipt и UTC boundary. Перед чтением Luna подтверждает все
digests; mismatch останавливает task как `BLOCKED`, без fallback на `HEAD`.

## Allowed reads

- эта карточка и batch-002 manifest;
- ровно десять holder blobs из `corpus_commit` и соответствующие 20 frozen F2
  rows;
- полный prior Wiki tree и batch-001 receipt/changeset;
- pinned OpenViking v0.4.16 LLM Wiki Skill.

Project docs, code, skills и знания, упомянутые внутри цитат, не являются
semantic input и не открываются ради Wiki. Process instructions можно читать
только для выполнения task; их content не становится Wiki evidence.

## Wiki semantics

- Wiki — производная библиотека того, что владелец сказал, а не project canon.
  `index.md` кратко называет эту границу и текущий processed boundary.
- Страница отвечает на один самостоятельный durable retrieval-вопрос. Это
  смысловая граница, не лимит: число страниц, длина любого файла и total output
  ничем не ограничены.
- Сохраняй полезное prior knowledge, если новые records его не изменяют.
  Дополнение с тем же retrieval-purpose обновляет существующую страницу;
  superseded формулировка исчезает из current Wiki, а история остаётся в
  quotes и changeset/receipts.
- Пересказ, объединение и новая формулировка разрешены. Для каждого
  материального факта, causal relation, scope, status, recommendation и
  relationship назови supporting record IDs. Неподдержанное не пиши; нужный
  inference отдели явно и назови evidence/uncertainty.
- `latest` не означает `current` автоматически. Неразрешённую актуальность
  оставляй неизвестной; не превращай её в уверенную инструкцию.
- Wiki ссылается только на chat-recall quotes и внутренние Wiki pages. Она не
  ссылается на project knowledge corpus, внешние URLs или файлы, названные в
  цитатах, и не копирует длинные цитаты.
- Index остаётся первым маршрутом: перечисляет все active pages и даёт
  различимые retrieval cues. Writer self-check не доказывает findability.

## Two-phase write gate

### Phase A — semantic draft

Luna пишет только
`experiments/openviking-chat-recall/artifacts/chronological-pilot/batch-002/changeset.json`.
Текущий Wiki tree не меняется. Changeset содержит:

- ordered operations `create | update | supersede | no-change | reject`;
- для затронутого page: path, page type, prior SHA-256 или `null`, полный
  proposed UTF-8 content и proposed SHA-256;
- `material_claims`: claim ID, краткое statement, epistemic kind
  `source-backed | inference | uncertainty`, supporting record IDs;
- coverage с ровно одной disposition на каждый из 20 new record IDs и полем
  `checked_prior_pages`: какие prior pages сверены на конфликт либо почему
  список пуст;
- причину page match/split и список prior claims/source links, которые
  сохраняются, меняются или удаляются.

Конфликт нового record с любой prior page обязан породить operation над этой
page либо явный unresolved-conflict status, видимый в current page/index.

Root отклоняет draft при missing/extra record, unsupported claim, silent
project enrichment, stale superseded prose, несоответствии prior SHA или
size-driven сокращении. Missing/unexplained `checked_prior_pages` тоже
отклоняет draft. До отдельного follow-up Luna не пишет Wiki/receipt.

### Phase B — exact materialization

После root follow-up Luna записывает proposed content из accepted changeset
byte-for-byte в текущий
`experiments/openviking-chat-recall/artifacts/chronological-pilot/current/wiki/**`
и создаёт
`experiments/openviking-chat-recall/artifacts/chronological-pilot/batch-002/receipt.json`.
Удаление active page допустимо только named supersede operation. Receipt
фиксирует before/after tree digests, exact content-SHA equality с draft,
operation/coverage counts, source addresses, diagnostic size metrics, model и
gaps. Quotes и hidden reasoning в receipt запрещены.

## Exact ownership

Тот же visible Luna thread работает без branch/worktree и без subagents. Его
write-set ограничен:

- current Wiki root `current/wiki/**` только в Phase B;
- `batch-002/changeset.json`;
- `batch-002/receipt.json` только в Phase B.

Plans, holders, F1–F3 artifacts, scripts, tests и unrelated dirty files не
меняются. Luna не коммитит и не пушит; root принимает и фиксирует checkpoint.

## Acceptance and next gate

Root независимо проверяет manifest membership/digests, exact coverage,
claim→record support, отсутствие project-corpus enrichment, removal of stale
superseded content, draft/materialized SHA equality и Wiki index integrity.
Для каждого нового record root проверяет `checked_prior_pages` либо адресную
причину пустого списка; найденный cross-page conflict не может остаться только
в changeset.
Отдельный blind reader начинает только с `index.md`, выбирает first page для
paraphrased вопросов и открывает не больше реально нужных Wiki pages.

Batch-002 принят только как второй checkpoint. Продолжение к batch-003 требует
наблюдаемого verdict по findability и хотя бы одному реальному update,
supersede либо честному `no applicable change`; create-only smooth prose не
доказывает serial currentness.

## Instruction trace

Естественный дефолт writer-а — оптимизировать размер, красиво обобщить и сразу
перезаписать Markdown. Компетентный ход — сначала предъявить source-backed
semantic delta, затем отдельно материализовать проверенный draft. Наблюдаемый
результат: нет size gate; каждый material claim адресован; Wiki bytes совпадают
с accepted changeset. Это вытесняет прежние hard compression thresholds и
неполный changeset, который нельзя было replay-ить без скрытого writer state.
