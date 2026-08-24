---
эпик: "самостоятельный experiment: openviking-chat-recall"
kind: context
записано: 2026-08-21
пересобрано: 2026-08-22
---

# Контекст — зачем нужна Wiki из chat-recall

## Проблема

`chat-recall` надёжно хранит точные датированные слова владельца, но это руда,
а не текущая картина знаний. Повторы и поздние corrections заставляют нового
агента снова читать много holders и самостоятельно собирать финальную позицию.

Если batch writer на шаге 100 перечитывает первые 990 источников, система
масштабируется хуже самого recall. Поэтому current Wiki обязана быть сжатой
памятью уже обработанного прошлого: новый writer читает только десять новых
holders и релевантные страницы Wiki.

Owner evidence:
`_ops/chat-recall/raw/2026-08-21-133152-codex-01a0236d.md:21-24,35,40-42,64-73`.

## Ожидаемый эффект

Новая сессия начинает с `index.md`, быстро выбирает нужную страницу, узнаёт
актуальную позицию владельца и при необходимости открывает точную исходную
цитату. Для большинства рабочих вопросов ей не нужно восстанавливать всю
хронологию или читать project corpus.

Wiki остаётся производной: её можно удалить и пересобрать. Она не заменяет
holders, не становится вторым проектным каноном и не скрывает, что знания
получены из речи владельца.

## Почему именно этот маршрут

OpenViking дал полезную information architecture и progressive context layers,
но stock runtime не образовал совместимую проверяемую цепочку. Поэтому проект
использует pinned prompts/IA, а snapshot, batching, provenance, validation,
resume и receipts реализует локально.

Последовательный chronological fold сохраняет одну current Wiki: каждый batch
видит новый evidence и уже дистиллированный prior, обновляет существующие
страницы и создаёт новые только для самостоятельных retrieval-вопросов. Это
избегает merge конфликтующих эпох и не заставляет агента перечитывать старые
quotes.

## Границы смысла

- Holders владеют точными словами, датами и историей.
- Deterministic manifests владеют membership, counts, hashes и provenance.
- Versioned prompt владеет semantic writing behavior.
- Current Wiki владеет только пересобираемым актуальным пересказом.
- `task.md` владеет системой и путём до конца; `status.md` — только frontier;
  `HISTORY.md` — только прошлым.

Пересказ неизбежно генерирует новую формулировку. Граница качества — не
буквальность, а отсутствие нового неподдержанного actor, subject, scope,
modality, relation, causality или status.

## Отпавшие ходы

- **Stock OpenViking runtime:** SDK/Compile route не дал совместимой
  воспроизводимой поверхности.
- **Один prompt на весь corpus:** не помещается устойчиво и скрывает coverage.
- **Повторное чтение всех prior quotes:** не масштабируется; current Wiki и
  deterministic prior bindings должны полностью заменить его.
- **Parallel writers по эпохам:** их outputs нельзя надёжно merge при
  corrections и supersession.
- **Source-by-source summaries:** дублируют holders, а не создают knowledge IA.
- **Project-file enrichment:** превращает Wiki owner speech во второй canon.
- **Repair rejected candidate:** доказывает ручную доводку output, а не качество
  повторяемого механизма.

Подробная история проверок и поворотов находится только в `HISTORY.md`.
