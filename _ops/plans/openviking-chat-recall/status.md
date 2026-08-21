---
эпик: "самостоятельный experiment: openviking-chat-recall"
состояние: в работе
режим: Wayfinding
обновлено: 2026-08-21
kind: status
---

# Статус — OpenViking Wiki для chat-recall

## Next

Выполнить typed-evidence probe на двух замороженных кластерах по
`modules/wave-3-typed-evidence-probe.md`. До его verdict не запускать full
corpus и не строить полный wrapper.

## Текущее состояние

- Rationale одобрен владельцем 2026-08-21; approval записан в
  `_ops/chat-recall/2026-08-21-133152-codex-01a0236d.md`.
- Там же владелец одобрил следующий route: узкий typed-evidence
  probe перед полным wrapper.
- После approval-capture corpus содержит 182 Markdown holder без `README.md`;
  точный frozen inventory и digest обязан записать writer.
- Stock route выбран как `add-resource` → официальный LLM Wiki Skill →
  `compile`; realtime memory/plugin route исключён.
- Исходные holders остаются source evidence; будущая Wiki — derived projection.
- Graphiti не выполняется как живая pinned задача и остаётся baseline по
  артефактам существующего эксперимента.
- Retrieval denominator locked до чтения Wiki: 11 exact questions, closed gold,
  matched budget, scoring и hard failures записаны в
  `modules/return-wave-1-retrieval-contract.md`.
- Runtime pilot интегрирован commit `d57a49d`: stock Compile blocked HTTP 400
  из-за несовместимости VikingBot/SDK; disposable shim построил diagnostic Wiki
  из семи страниц, но это не stock acceptance.
- Blind v1 diagnostic failed: source arm нашёл current OpenViking outcome, Wiki
  arm подменил его historical retrieval-script задачей; обе руки abstained на
  no-gold control. Return: `modules/return-wave-2-v1-diagnostic.md`.
- V2 diagnostic integrated commit `4faf469`: exact approved reason создал три
  pages, включая шесть counted recurrence sections и отдельный outcome page;
  semantic audit отклонил результат: 4 FAIL, 1 UNKNOWN, 1 PASS, outcome
  inversion. Return: `modules/return-wave-2-v2-audit.md`.

## Вехи

| Веха | Статус | Evidence |
| --- | --- | --- |
| 1. Pilot runtime | ⚠️ blocked | Stock receipt + diagnostic Wiki: `d57a49d` |
| 2. Pilot audit | ❌ | V1/V2 blind + semantic returns: current Wiki rejected |
| 3. Typed-evidence probe | 🔄 | Одобрен; карточка wave 3 зафиксирована |
| 4. Full backfill | заблокировано | Только после положительного pilot-verdict |
| 5. Handoff | заблокировано | Только после принятого full audit |

## Thread registry

- `wave-1-runtime-pilot.md` — единственный writer runtime/experiment;
  retained pinned task `01a023c3-ee43-7c73-964a-08a496494398`,
  «OpenViking: собрать stock pilot»; recovery-only: worktree отстал и
  содержит незавершённые файлы, поэтому не переиспользуется.
- `wave-1-retrieval-contract.md` — независимый read-only acceptance designer;
  task `01a023c3-ee43-7c73-964a-08b22a2d1b17`; ✅ return принят, archived.
- `wave-2-diagnostic-retrieval.md` — blind Wiki arm task
  `01a023e9-f36e-7471-86f5-d9ae99828de2`, «OpenViking: blind Wiki arm»;
  source arm task `01a023e9-f36c-71c1-b216-f5fb84e1310e`; ✅ return записан,
  both archived.
- `wave-2-v2-audit.md` — blind v2 reader task
  `01a023fa-177f-7010-8e1f-121ccd352951`, «OpenViking: blind Wiki v2 arm»;
  semantic auditor task `01a023fa-1782-7563-979e-74a6428dde87`; ✅ return
  записан, both archived.
- `wave-3-typed-evidence-probe.md` — Luna Max writer в чистом worktree;
  pinned task `01a02465-8638-7d41-b1a5-8c91a9becd72`,
  «OpenViking: typed-evidence probe». Blind reader запускается только после
  интеграции writer return.

## Открытые вопросы владельцу

Нет. Следующее решение появится только после измеренного verdict
typed-evidence probe.
