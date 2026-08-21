---
kind: module-return
scope: openviking-chat-recall-trajectory
date: 2026-08-21
state: accepted-route-correction
---

# Fresh Eyes — utility после ingestion

## Вопрос

Продолжать ли чинить pre-build Wave 5 acceptance harness или переходить к
сборке Wiki. Ответ менял dependency gate полного compiler-а.

## Разные линзы

- Ladder: после одного bounded operations repair дальнейшее усиление Wave 5
  перестаёт служить полной Wiki; falsifier — новый semantic hard failure.
- Solvent: G0 нужен перед semantic writers, но не обязан сериализовать
  deterministic snapshot/evidence; falsifier — перенос semantic ошибки в
  дорогой full backfill.
- Prospector: официальный OpenViking RAG benchmark сначала выбирает
  воспроизводимый sample, затем ingest-ит его и измеряет Recall, F1, Accuracy,
  latency и token usage. Static validator до ingestion utility не доказывает.
- Claude Opus 5 Premortem: текущая дизъюнкция могла принять экономию tokens при
  росте reads и wall time. Первый matched run уже показал этот сигнал.

## Решение

Wave 5 замораживает semantic gold и claim/currentness contract. Wave 6 строит
детерминированный frozen foundation без pre-build utility PASS. Новый Wave 6b
ingest-ит representative frozen subset в настоящий L2/L1/L0 route и только
потом выполняет 5 × 2 fresh matched runs. PASS требует non-inferior semantics,
улучшения минимум одной основной cost axis и отсутствия material regression на
других. Только этот PASS открывает full semantic Wave 7.

## Альтернативы

- Пропустить utility probe: быстрее начать full build, но поздно обнаружить
  route, который только добавляет hop.
- Продолжить старый harness: улучшить protocol до ingestion, но не проверить
  пользовательскую поверхность.

## Evidence

- owner outcome: `_ops/chat-recall/2026-08-21-133152-codex-01a0236d.md`;
- empirical-search criterion:
  `_ops/chat-recall/2026-08-20-181330-claude-a7539038.md`;
- representative real-ingest criterion:
  `_ops/chat-recall/2026-08-18-151822-codex-01a0145e.md`;
- first matched failure: `wave-5-matched-grader.md`;
- upstream sequence and metrics:
  `https://github.com/volcengine/OpenViking/blob/main/benchmark/RAG/README.md`.

## Gap

Новый Wave 6b contract и его execution ещё не приняты. Dirty holder overlays
не позволяют молча считать текущий `HEAD` полным corpus snapshot.
