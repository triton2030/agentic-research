# Маршрутная таблица — 94 единицы инвентаря отрицаний

Источник инвентаря: `../B-negations-instruction-layer.md`. Все пути ниже —
относительно `IL-cand-1/`; reference-файлы лежат в `references/`.

## Строки ядра, работающие как маршрут

| ID | Строка `SKILL.md` |
|---|---|
| K1 | «Рабочее состояние: `admission → chain map → owner → steering cell → control → exact delta → proof`. Каждый gate порождает свой наблюдаемый результат до следующего; **читай его файл в момент прохождения, не по памяти**. Пропустить gate можно только когда его результат уже прямо подтверждён текущим evidence.» |
| K2 | «Файлы в `references/`, по одному на момент: `product-measure.md` (до всего…), `controller.md`, `steering-cell.md` (до wording), `gate0-admission.md`, `gate1-chain.md`, `gate2-owner.md`, `gate3-cell.md`, `gate4-control.md`, `gate5-wording.md`, `gate6-bypass.md`, `gate6-proof.md`, `triggered-rules.md` (cold `_ops/rules/**`), `output-stop.md` (перед вердиктом).» |
| K3 | «Условная глубина — только по условию, названному в файле gate: `discovery-*.md`, `placement-*.md`, `meaning-*.md`, `language-*.md`, `divergences-*.md`, `cli-recipes.md`, `demo-contrastive.md`.» |
| K4 | Блок `## Boundaries` (5 строк, дословно из оригинала) — живёт в ядре целиком. |

Второй хоп (строка gate-файла, открывающая условную глубину) назван в колонке
«хоп»; он перенесён дословно, изменено только имя файла в указателе
(канонизация указателя после разреза файла).

## A. Режим и допуск durable работы

| # | Файл назначения | Маршрут из ядра | Хоп | Показ |
|---|---|---|---|---|
| N01 | `gate0-admission.md` (п. 1); дубли перенесены вместе с носителями: `product-measure.md`, `cli-recipes.md`, `meaning-zone.md`, `placement-scope.md`, `placement-protocol.md` (п. 5) | K2 → `gate0-admission` | — | |
| N02 | `gate0-admission.md` п. 2 | K2 | — | |
| N03 | `gate0-admission.md` п. 3 | K2 | — | |
| N04 | `gate0-admission.md` п. 4 | K2 | — | |
| N05 | `gate0-admission.md` п. 5 | K2 | — | |
| N06 | `gate0-admission.md` п. 6 | K2 | — | |
| N07 | `gate0-admission.md` «Результат gate» | K2 | — | показ |
| N08 | `gate0-admission.md` п. 7 | K2 | — | |

## B. Effective chain

| # | Файл назначения | Маршрут из ядра | Хоп | Показ |
|---|---|---|---|---|
| N09 | `gate1-chain.md` п. 1 | K2 → `gate1-chain` | — | |
| N10 | `gate1-chain.md` п. 2; дубль — таблица «Что Грузится Когда» в `discovery-loading.md` | K2 / K3 | Gate 1.3 | |
| N11 | `gate1-chain.md` п. 3 | K2 | — | |
| N12 | `gate1-chain.md` п. 5 | K2 | — | |
| N13 | `gate1-chain.md` п. 6 | K2 | — | |
| N14 | `gate1-chain.md` п. 7 | K2 | — | |
| N15 | `gate1-chain.md` «Результат gate» | K2 | — | показ |

## C. Owner и класс delta

| # | Файл назначения | Маршрут из ядра | Хоп | Показ |
|---|---|---|---|---|
| N16 | `gate2-owner.md` п. 1 | K2 → `gate2-owner` | — | |
| N17 | `gate2-owner.md` п. 2 | K2 | — | |
| N18 | `gate2-owner.md` п. 3; дубли — `placement-scope.md` п. 1, `language-failure-modes.md` (Text-level duplicate) | K2 / K3 | Gate 1.7, Gate 5.11 | |
| N19 | `gate2-owner.md` п. 3 + `gate5-wording.md` п. 7; дубли — `placement-scope.md` п. 2, `language-judgment.md` п. 4 | K2 / K3 | Gate 1.7, Gate 5.11 | |
| N20 | `gate2-owner.md` п. 4 | K2 | — | |
| N21 | `gate2-owner.md` п. 5 | K2 | — | |
| N22 | `gate2-owner.md` п. 6; дубли — K4 в ядре, `placement-protocol.md` п. 2 | K2 + K4 | Gate 1.7 | |
| N23 | `gate2-owner.md` «Результат gate» | K2 | — | показ |

## D. Steering cell

| # | Файл назначения | Маршрут из ядра | Хоп | Показ |
|---|---|---|---|---|
| N24 | `steering-cell.md` | K2 → `steering-cell` (до wording) | — | |
| N25 | `steering-cell.md`; дубль — `divergences-donot-stop.md` | K2 / K3 | Gate 6.8 → `divergences-contract.md` → «Запреты и stop» | |
| N26 | `steering-cell.md` (Natural continuation) + `gate3-cell.md` п. 4 | K2 | — | |
| N27 | `steering-cell.md` (последний абзац) | K2 | — | |
| N28 | `steering-cell.md` + `gate3-cell.md` «Результат gate» | K2 | — | показ (вторая половина) |
| N29 | `gate3-cell.md` п. 3 | K2 → `gate3-cell` | — | |
| N30 | `gate3-cell.md` п. 1 | K2 | — | |
| N31 | `gate3-cell.md` п. 7 + `gate5-wording.md` п. 9; дубль — `language-failure-modes.md` (Accidental mandate / Hyrum) | K2 / K3 | Gate 5.11 | |
| N32 | `gate3-cell.md` п. 8 | K2 | — | |
| N33 | `gate3-cell.md` п. 9; дубли — `cli-recipes.md` («router, а не второй runbook»; «Не дублируй его commands…») | K2 / K3 | Gate 3.9, Gate 6.9 | |

## E. Control и выбор repair

| # | Файл назначения | Маршрут из ядра | Хоп | Показ |
|---|---|---|---|---|
| N34 | `product-measure.md` + `gate4-control.md` пп. 1–2; дубли — `meaning-protocol.md` п. 6, `discovery-limits-placement.md` (Placement Rules) | K2 / K3 | Gate 1.3, Gate 3.9 | |
| N35 | `language-failure-modes.md` (Risk-word overclaim) | K3 | Gate 5.11 | |
| N36 | `discovery-loading.md` | K3 | Gate 1.3 | |
| N37 | `gate4-control.md` п. 3 (все семь вариантов repair целиком в одном файле) | K2 → `gate4-control` | — | |
| N38 | `gate4-control.md` п. 4; дубли — `language-judgment.md` п. 3, `placement-findings.md` | K2 / K3 | Gate 1.7, Gate 5.11 | |
| N39 | `gate4-control.md` п. 5; дубли — `meaning-protocol.md` п. 4, `divergences-contract.md` п. 3 | K2 / K3 | Gate 3.9, Gate 6.8 | |
| N40 | `gate4-control.md` «Результат gate» | K2 | — | показ |

## F. Wording exact delta

| # | Файл назначения | Маршрут из ядра | Хоп | Показ |
|---|---|---|---|---|
| N41 | `gate5-wording.md` п. 1 | K2 → `gate5-wording` | — | |
| N42 | `gate5-wording.md` п. 2 | K2 | — | |
| N43 | `gate5-wording.md` п. 3 | K2 | — | |
| N44 | `gate5-wording.md` п. 4 | K2 | — | |
| N45 | `gate5-wording.md` п. 5 | K2 | — | |
| N46 | `gate5-wording.md` п. 6; дубль — `meaning-protocol.md` п. 6 | K2 / K3 | Gate 3.9 | |
| N47 | `gate5-wording.md` п. 7; дубли — `placement-protocol.md` п. 4, `placement-scope.md` п. 3 | K2 / K3 | Gate 1.7 | |
| N48 | `gate5-wording.md` п. 8 | K2 | — | |
| N49 | `gate5-wording.md` п. 9; дубль — `meaning-design-mode.md` п. 3 | K2 / K3 | Gate 3.9 | |
| N50 | `gate5-wording.md` п. 10 | K2 | — | |
| N51 | `gate5-wording.md` п. 11 | K2 | — | |
| N52 | `language-failure-modes.md` (Literal scope) | K3 | Gate 5.11 | |
| N53 | `language-failure-modes.md` (Frame capture / sycophancy) | K3 | Gate 5.11 | |
| N54 | `language-failure-modes.md` (Lost-in-the-middle) | K3 | Gate 5.11 | |

## G. Bypass и доказательство

| # | Файл назначения | Маршрут из ядра | Хоп | Показ |
|---|---|---|---|---|
| N55 | `gate6-bypass.md` п. 1 | K2 → `gate6-bypass` | — | |
| N56 | `gate6-bypass.md` п. 2 | K2 | — | |
| N57 | `gate6-bypass.md` п. 3 | K2 | — | |
| N58 | `gate6-bypass.md` п. 4; дубль — `divergences-donot-stop.md` | K2 / K3 | Gate 6.8 | |
| N59 | `gate6-proof.md` п. 5 | K2 → `gate6-proof` | — | |
| N60 | `gate6-proof.md` п. 6 | K2 | — | |
| N61 | `gate6-proof.md` п. 7; дубли — `product-measure.md`, `output-stop.md` | K2 | — | показ (дубль в `output-stop`) |
| N62 | `gate6-proof.md` п. 7 (вторая половина) | K2 | — | |
| N63 | `gate6-proof.md` п. 8; дубль — `language-judgment.md` (Готово, когда…) | K2 / K3 | Gate 5.11 | |
| N64 | `gate6-proof.md` п. 9 | K2 | — | |
| N65 | `gate6-proof.md` «Результат gate» + `output-stop.md` | K2 | — | показ |

## H. Controller

| # | Файл назначения | Маршрут из ядра | Хоп | Показ |
|---|---|---|---|---|
| N66 | `controller.md`; дубль-усилитель — K1 в ядре | K1 + K2 | — | |
| N67 | `controller.md` | K2 → `controller` | — | |
| N68 | `controller.md` | K2 | — | |
| N69 | `controller.md` | K2 | — | показ (запрет на длинную анкету) |
| N70 | `controller.md` | K2 | — | |
| N71 | `controller.md` | K2 | — | |
| N72 | `demo-contrastive.md` | K3 | «Контрастивная демонстрация механизма — `demo-contrastive.md`» в `gate5-wording.md` | показ |

## I. Triggered Repository Rules

| # | Файл назначения | Маршрут из ядра | Хоп | Показ |
|---|---|---|---|---|
| N73 | `triggered-rules.md` | K2 → `triggered-rules` (cold `_ops/rules/**`) | — | |
| N74 | `triggered-rules.md` | K2 | — | |
| N75 | `triggered-rules.md` | K2 | — | |
| N76 | `triggered-rules.md` | K2 | — | |
| N77 | `triggered-rules.md` | K2 | — | |
| N78 | `triggered-rules.md` | K2 | — | |
| N79 | `triggered-rules.md`; смежная строка про `1skill-architect` — K4 в ядре | K2 + K4 | — | |

## J. Границы, universalization, локальные нормы references

| # | Файл назначения | Маршрут из ядра | Хоп | Показ |
|---|---|---|---|---|
| N80 | **ядро**, блок `## Boundaries` | K4 (сама единица) | — | |
| N81 | **ядро**, блок `## Boundaries`; дубль — `meaning-protocol.md` п. 3 | K4 (сама единица) | Gate 3.9 | |
| N82 | `output-stop.md` | K2 → `output-stop` (перед вердиктом) | — | показ |
| N83 | `placement-protocol.md` п. 4; дубли — `discovery-loading.md`, `discovery-limits-placement.md`, `meaning-protocol.md` п. 5, `meaning-zone.md` | K3 | Gate 1.3, Gate 1.7, Gate 3.9 | |
| N84 | `placement-findings.md`; дубль — `language-judgment.md` п. 1 | K3 | Gate 1.7 → `placement-protocol.md` → `placement-findings.md`; Gate 5.11 | показ |
| N85 | `placement-scope.md` п. 3 | K3 | Gate 1.7 | |
| N86 | `placement-protocol.md` п. 3; дубль — `cli-recipes.md` | K3 | Gate 1.7, Gate 6.9 | |
| N87 | `placement-protocol.md` пп. 5–6; дубль — `cli-recipes.md` | K3 | Gate 1.7, Gate 6.9 | |
| N88 | `discovery-limits-placement.md` (Placement Rules) | K3 | Gate 1.3 | |
| N89 | `discovery-loading.md` (`AGENTS.md` — Optional Shared Owner) | K3 | Gate 1.3 | |
| N90 | `discovery-limits-placement.md` (Description Limits) | K3 | Gate 1.3 | |
| N91 | `meaning-protocol.md` пп. 1–2 + `meaning-findings.md` | K3 | Gate 3.9 → `meaning-protocol.md` → `meaning-findings.md` | показ (часть в findings) |
| N92 | `meaning-design-mode.md` пп. 2, 5 | K3 | Gate 3.9 | |
| N93 | `meaning-design-mode.md` пп. 1, 4 | K3 | Gate 3.9 | |
| N94 | `divergences-contract.md` + `divergences-donot-stop.md` | K3 | Gate 6.8 | показ (Stop-блок) |

## Итог

- Единиц инвентаря: **94**.
- Живут в ядре: **2** (N80, N81 — блок `Boundaries` перенесён в ядро дословно).
- Живут в reference с маршрутом из ядра: **92**.
- Удалено: **0**. Записей «удалена: причина» нет — ни одна единица не снята.

## Блоки, помеченные «показ» (перенесены дословно, сжатию не подлежат)

`output-stop.md` целиком (шаблон вердикта + условие готовности + стоп);
все семь строк «**Результат gate:**» (gate 0–6, decision trace каждого gate);
`placement-findings.md` (Findings — формат + Выход);
`meaning-findings.md` (Findings — формат + Выход);
`language-judgment.md` (Findings Contract, код-блок);
`divergences-donot-stop.md` (Stop);
`cli-recipes.md` (Instruction-Layer Delta — пакет полей, возвращаемый наружу);
`controller.md` (запрет публиковать decision trace как длинную анкету);
`demo-contrastive.md` (контрастивная демонстрация).

## Что изменено помимо переноса

1. **Канонизация указателей.** В перенесённых строках заменены только имена
   файлов: `claude-discovery.md` → `discovery-loading.md` /
   `discovery-limits-placement.md`; `audit-placement-structure.md` →
   `placement-scope.md` / `placement-protocol.md`; `audit-meaning-criteria.md` →
   `meaning-protocol.md` / `meaning-design-mode.md`; `language-quality-audit.md`
   → `language-failure-modes.md`; `llm-divergences.md` →
   `divergences-contract.md`. Текст вокруг указателя не тронут.
2. **Смена уровня заголовка** у секций, ставших отдельными файлами.
3. **Новые строки — только маршрутные**: «Далее: …», «Определение cell — …»,
   `read-when`-frontmatter у частей разрезанных reference-файлов. Ни одна
   нормативная формулировка не переписана.
4. **Нумерация Gate 6** сохранена сквозной: `gate6-bypass.md` — пп. 1–4,
   `gate6-proof.md` — пп. 5–10 и «Результат gate». Пара «design-time proxy —
   не повышай proxy до доказательства» (п. 5 + путь отказа) намеренно оставлена
   в одном файле.
