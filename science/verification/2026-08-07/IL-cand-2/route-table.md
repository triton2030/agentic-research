# Маршрутная таблица — IL-cand-2

Источник инвентаря: `../B-negations-instruction-layer.md`, 94 единицы.
Удалено: **0**. Все 94 перенесены дословно; изменения текста ограничены
уровнем заголовка (`###` → `#`) и префиксом ссылок (`references/x.md` → `x.md`),
плюс один перенос двух предложений из `Controller` в ядро (см. C2).

## Легенда маршрутов

Строки ядра (`SKILL.md`), посылающие в файл в момент действия:

| Метка | Строка ядра |
|---|---|
| `C1` | «Этот controller владеет методом мышления; references владеют только условной глубиной.» — живёт в ядре |
| `C2` | «Держи компактное рабочее состояние `admission → chain map → owner → steering cell → control → exact delta → proof`. Каждый gate должен породить свой наблюдаемый результат до следующего. Пропустить gate можно только когда его результат уже прямо подтверждён текущим evidence; гладкий финальный текст не заменяет промежуточное различение.» — живёт в ядре |
| `R-pre` | «До Gate 0 прочитай `product-jobs.md` (продукт, мера, режимы `audit`/`change`, границы) и `controller.md` (три failure-а иерархии, re-anchor, decision traces).» |
| `R0` | «- Gate 0 допуск durable работы — `gate0-admission.md`» |
| `R1` | «- Gate 1 effective chain map — `gate1-chain.md`» |
| `R2` | «- Gate 2 owner и класс delta — `gate2-owner.md`» |
| `R3` | «- Gate 3 steering cell — `gate3-steering.md`» |
| `R4` | «- Gate 4 control и один repair — `gate4-control.md`» |
| `R5` | «- Gate 5 exact delta — `gate5-wording.md`» |
| `R6` | «- Gate 6 bypass и доказательство — `gate6-bypass.md`, затем `gate6-proof.md`» |
| `R-out` | «Перед финальным ответом открой `output-stop.md`: формат вывода, условия готовности и стоп.» |

Продолжения маршрута внутри файла (второй и третий уровень), все —
исходные условные маршруты, перенесённые дословно, кроме помеченных `нов.`:

| Метка | Где стоит | Куда посылает |
|---|---|---|
| `r1.3` | `gate1-chain.md` п. 3 | `claude-discovery.md` — «только когда они спорны» |
| `r1.7` | `gate1-chain.md` п. 7 | `audit-placement-structure.md` — «до owner-решения» |
| `r2.0` | `gate2-owner.md`, шапка (нов.) | `triggered-rules.md` |
| `r3.0` | `gate3-steering.md`, шапка (нов.) | `steering-cell.md` — «до пункта 1» |
| `r3.9` | `gate3-steering.md` п. 9 | `audit-meaning-criteria.md` |
| `r5.11` | `gate5-wording.md` п. 11 | `language-quality-audit.md` — «до финального wording» |
| `r6.8` | `gate6-proof.md` п. 8 | `llm-divergences.md` |
| `r6.9` | `gate6-proof.md` п. 9 | `cli-recipes.md` |
| `r6.b` | `gate6-bypass.md`, хвост (нов.) | `gate6-proof.md` |
| `rAM` | `audit-meaning-criteria.md` (нов.) | `meaning-protocol.md`, `meaning-design-mode.md` |
| `rAP` | `audit-placement-structure.md` (нов.) | `placement-protocol.md` |
| `rCD` | `claude-discovery.md` (нов.) | `claude-discovery-placement.md` |
| `rLQ` | `language-quality-audit.md` (нов.) | `language-quality-findings.md` |
| `rLD` | `llm-divergences.md` (нов.) | `llm-divergences-stop.md` |

`показ` — блок, чей видимый выход адресован владельцу; перенесён дословно,
без владельца не сжимается.

## Таблица единиц

| # | Единица (метка) | Файл назначения | Маршрут | показ |
|---|---|---|---|---|
| N01 | audit не меняет files / change — только scoped repair | `gate0-admission.md`; `product-jobs.md`; `gate6-proof.md` п.10; `cli-recipes.md`; `audit-meaning-criteria.md`; `audit-placement-structure.md`; `placement-protocol.md` п.5 | `R0`, `R-pre`, `R6`, `r6.9`, `r3.9`, `r1.7`+`rAP` | показ (bullets режимов) |
| N02 | одноразовое vs durable | `gate0-admission.md` | `R0` | |
| N03 | основание durable candidate | `gate0-admission.md` | `R0` | |
| N04 | framing/уверенность не evidence | `gate0-admission.md` | `R0` | |
| N05 | не достраивай premise reasoning-ом | `gate0-admission.md` | `R0` | |
| N06 | только проваленные jobs | `gate0-admission.md` (+ определения jobs в `product-jobs.md`) | `R0`, `R-pre` | |
| N07 | нет основания → не добавляй правило | `gate0-admission.md` («Результат gate») | `R0` | показ |
| N08 | выбор surface → `1skill-architect` | `gate0-admission.md` | `R0` | |
| N09 | разные chain в разных runner-ах | `gate1-chain.md` | `R1` | |
| N10 | только реально загружаемые; `file exists` ≠ `text reaches` | `gate1-chain.md`; `claude-discovery.md` (таблица «Что Грузится Когда») | `R1`, `r1.3` | |
| N11 | discovery — только когда спорно; не переноси привычку runtime | `gate1-chain.md` п.3 | `R1` | |
| N12 | runtime winner ≠ semantic owner | `gate1-chain.md` | `R1` | |
| N13 | winner из loading+precedence, не из имени файла | `gate1-chain.md` | `R1` | |
| N14 | placement спорен → читать до owner-решения | `gate1-chain.md` п.7 | `R1` → `r1.7` | |
| N15 | не доказал loading → назови gap | `gate1-chain.md` («Результат gate») | `R1` | показ |
| N16 | scope trigger-а, не папка находки | `gate2-owner.md` | `R2` | |
| N17 | самый узкий existing owner | `gate2-owner.md` | `R2` | |
| N18 | один source of meaning | `gate2-owner.md`; `audit-placement-structure.md` п.1; `language-quality-audit.md` (Text-level duplicate) | `R2`, `r1.7`, `r5.11` | |
| N19 | refresher только в другом lifecycle moment | `gate2-owner.md`; `gate5-wording.md` п.7; `audit-placement-structure.md` п.2; `language-quality-findings.md` п.4 | `R2`, `R5`, `r1.7`, `r5.11`+`rLQ` | |
| N20 | не присваивай authority соседей | `gate2-owner.md` | `R2` | |
| N21 | класс delta (fact/rule/invariant) | `gate2-owner.md` | `R2` | |
| N22 | container → `1ia-audit`, стоп до edits | `gate2-owner.md`; `product-jobs.md` (Boundaries); `placement-protocol.md` п.2 | `R2`, `R-pre`, `r1.7`+`rAP` | |
| N23 | нет owner-а → delete/no-op, не wording | `gate2-owner.md` («Результат gate») | `R2` | показ |
| N24 | до wording — steering cell | `steering-cell.md` | `R3` → `r3.0` | |
| N25 | `MUST`/rationale/self-check не чинят causal gap | `steering-cell.md`; `llm-divergences-stop.md` (Do Not) | `R3`→`r3.0`, `r6.8`+`rLD` | |
| N26 | поведение, не скрытое состояние | `steering-cell.md`; `gate3-steering.md` п.4 | `R3`→`r3.0`, `R3` | |
| N27 | cell — scaffold, не формат целевой инструкции | `steering-cell.md` | `R3` → `r3.0` | |
| N28 | не назвал развилку → delta не доказана | `steering-cell.md`; `gate3-steering.md` («Результат gate») | `R3`→`r3.0`, `R3` | показ |
| N29 | прогон через old/default chain без правила задним числом | `gate3-steering.md` п.3 | `R3` | |
| N30 | разница видна до самоотчёта | `gate3-steering.md` п.1 | `R3` | |
| N31 | пример иллюстрирует, но не создаёт правило | `gate3-steering.md` п.7; `gate5-wording.md` п.9; `language-quality-audit.md` (Accidental mandate/Hyrum) | `R3`, `R5`, `r5.11` | |
| N32 | несколько изменений = несколько repairs | `gate3-steering.md` п.8 | `R3` | |
| N33 | reference — условная глубина, не копия protocol-а | `gate3-steering.md` п.9; `cli-recipes.md` | `R3`→`r3.9`, `r6.9` | |
| N34 | дорогой инвариант — на permission/hook/validator | `product-jobs.md`; `gate4-control.md` пп.1–2; `meaning-protocol.md` п.6; `claude-discovery-placement.md` (Placement Rules) | `R-pre`, `R4`, `r3.9`+`rAM`, `r1.3`+`rCD` | |
| N35 | risk-word overclaim | `language-quality-audit.md` | `R5` → `r5.11` | |
| N36 | `CLAUDE.md` — context, не enforced configuration | `claude-discovery.md` | `R1` → `r1.3` | |
| N37 | семь repair-вариантов по причине провала | `gate4-control.md` п.3 | `R4` | |
| N38 | один primary repair | `gate4-control.md` п.4; `language-quality-findings.md` п.3; `audit-placement-structure.md` (Findings) | `R4`, `r5.11`+`rLQ`, `r1.7` | |
| N39 | procedure только когда order/completeness — контракт | `gate4-control.md` п.5; `meaning-protocol.md` п.4; `llm-divergences.md` п.3 | `R4`, `r3.9`+`rAM`, `r6.8` | |
| N40 | не отличил repair от меньшего → бери меньший | `gate4-control.md` («Результат gate») | `R4` | показ |
| N41 | начинай с observable trigger/scope | `gate5-wording.md` п.1 | `R5` | |
| N42 | запрет без preferred continuation | `gate5-wording.md` п.2 | `R5` | |
| N43 | «осознай/будь внимателен» → наблюдаемый check | `gate5-wording.md` п.3 | `R5` | |
| N44 | check в point of action | `gate5-wording.md` п.4 | `R5` | |
| N45 | exception не становится вторым default | `gate5-wording.md` п.5 | `R5` | |
| N46 | evidence и stop против completion по пересказу | `gate5-wording.md` п.6; `meaning-protocol.md` п.6 | `R5`, `r3.9`+`rAM` | показ |
| N47 | pointer по умолчанию; rare depth — в cold owner | `gate5-wording.md` п.7; `audit-placement-structure.md` п.3; `placement-protocol.md` п.4 | `R5`, `r1.7`, `r1.7`+`rAP` | |
| N48 | rationale/example только по условию | `gate5-wording.md` п.8 | `R5` | |
| N49 | router ориентирует, не погружает | `gate5-wording.md` п.9; `meaning-design-mode.md` п.3 | `R5`, `r3.9`+`rAM` | |
| N50 | delete-first pass | `gate5-wording.md` п.10 | `R5` | |
| N51 | спорный wording → language audit до финала | `gate5-wording.md` п.11 | `R5` → `r5.11` | |
| N52 | literal scope | `language-quality-audit.md` | `R5` → `r5.11` | |
| N53 | frame capture / sycophancy | `language-quality-audit.md` | `R5` → `r5.11` | |
| N54 | line count сам finding не доказывает | `language-quality-audit.md` | `R5` → `r5.11` | |
| N55 | назови bypass до вердикта | `gate6-bypass.md` п.1 | `R6` | |
| N56 | bypass проходит → недостающий operator, не ещё один MUST | `gate6-bypass.md` п.2 | `R6` | |
| N57 | заранее назови expected old/proposed act и scoring | `gate6-bypass.md` п.3 | `R6` | |
| N58 | не меняй case/model/settings/правило одновременно | `gate6-bypass.md` п.4; `llm-divergences-stop.md` (Do Not) | `R6`, `r6.8`+`rLD` | |
| N59 | proxy для малой правки, cold-start для material | `gate6-bypass.md` п.5 | `R6` | |
| N60 | один run — возможность, не probability shift | `gate6-bypass.md` п.6 | `R6` | |
| N61 | self-report/шаблон не behavioral evidence | `gate6-proof.md` п.7; `product-jobs.md`; `output-stop.md` | `R6`→`r6.b`, `R-pre`, `R-out` | показ |
| N62 | same-model critique не независимая проверка | `gate6-proof.md` п.7 | `R6` → `r6.b` | |
| N63 | недатированная интуиция ≠ свойство модели | `gate6-proof.md` п.8; `language-quality-findings.md` («Готово, когда») | `R6`→`r6.8`, `r5.11`+`rLQ` | |
| N64 | evidence за пределами instruction files → routing | `gate6-proof.md` п.9 | `R6` → `r6.9` | |
| N65 | нет run-а → назови gap, не повышай proxy | `gate6-proof.md` («Результат gate»); `output-stop.md` | `R6`, `R-out` | показ |
| N66 | каждый gate даёт свой результат; пропуск только по подтверждённому evidence | **ядро `SKILL.md`** | `C2` | |
| N67 | три failure-а иерархии; поздний успех не доказывает ранний | `controller.md` | `R-pre` | |
| N68 | clean re-anchor | `controller.md` | `R-pre` | |
| N69 | decision traces, не длинная анкета | `controller.md` | `R-pre` | показ |
| N70 | классифицируй mitigation, не плоди prose-rule | `controller.md` | `R-pre` | |
| N71 | controller владеет методом, references — глубиной | **ядро `SKILL.md`** | `C1` | |
| N72 | контрастивная демонстрация механизма, не правило проекта | `steering-cell.md` | `R3` → `r3.0` | показ |
| N73 | cold rule directory допустима при трёх условиях | `triggered-rules.md` | `R2` → `r2.0` | |
| N74 | always-on в effective `AGENTS.md`, path-local в subtree | `triggered-rules.md` | `R2` → `r2.0` | |
| N75 | root — только trigger → RULE | `triggered-rules.md` | `R2` → `r2.0` | |
| N76 | steering cell реконструируется, не сериализуется | `triggered-rules.md` | `R2` → `r2.0` | |
| N77 | RULE без route — orphan; копия procedure — competing owner | `triggered-rules.md` | `R2` → `r2.0` | |
| N78 | читай RULE после совпадения trigger | `triggered-rules.md` | `R2` → `r2.0` | |
| N79 | жанр `2*` → `1local-rules` | `triggered-rules.md` | `R2` → `r2.0` | |
| N80 | scope/done/stop → `1goal`; task contract → `1planning` | `product-jobs.md` (Boundaries) | `R-pre` | |
| N81 | `depends-on`/anchors/cycles → `1md-graph` | `product-jobs.md` (Boundaries); `meaning-protocol.md` п.3 | `R-pre`, `r3.9`+`rAM` | |
| N82 | стоп до edits/mutation/внешней записи без intent | `output-stop.md` | `R-out` | показ |
| N83 | не универсализируй repo convention | `placement-protocol.md` п.4; `audit-placement-structure.md` п.3; `claude-discovery.md` (интро и `AGENTS.md`); `meaning-protocol.md` п.5 | `r1.7`+`rAP`, `r1.7`, `r1.3`, `r3.9`+`rAM` | |
| N84 | «звучит плохо» — вкус, не finding | `audit-placement-structure.md` (Findings); `language-quality-findings.md` п.1 | `r1.7`, `r5.11`+`rLQ` | показ |
| N85 | hot-path сверху; секции только когда меняют решение | `audit-placement-structure.md` п.3 | `R1` → `r1.7` | |
| N86 | results поиска — candidates до чтения bodies | `placement-protocol.md` п.3; `cli-recipes.md` | `r1.7`+`rAP`, `r6.9` | |
| N87 | closeout только после edits; не требуй чужой tool | `placement-protocol.md` пп.5–6; `cli-recipes.md` | `r1.7`+`rAP`, `r6.9` | |
| N88 | imports не экономят launch context | `claude-discovery-placement.md` | `r1.3` → `rCD` | |
| N89 | Claude Code читает `CLAUDE.md`, не `AGENTS.md` | `claude-discovery.md` | `R1` → `r1.3` | |
| N90 | не выдумывай failure mechanism превышения | `claude-discovery-placement.md` | `r1.3` → `rCD` | |
| N91 | прочитай зону; 2–4 пункта; критерий — outcome | `meaning-protocol.md` пп.1–2; `audit-meaning-criteria.md` (Findings) | `r3.9`+`rAM`, `r3.9` | показ (Findings) |
| N92 | probes — evals, их текст не вставляется в инструкцию | `meaning-design-mode.md` пп.2, 5 | `r3.9` → `rAM` | |
| N93 | «читать нечего» не бывает; subtree не ориентирует до загрузки | `meaning-design-mode.md` пп.1, 4 | `r3.9` → `rAM` | |
| N94 | только после наблюдённого failure; не family-wide; не стек инструкций | `llm-divergences.md` (frontmatter `read-when`, Contract 1–5); `llm-divergences-stop.md` (Do Not, Stop) | `R6`→`r6.8`, `r6.8`+`rLD` | показ (Stop) |

## Итог

- В ядре: **2** (N66, N71) плюс `description` как триггерная поверхность.
- В references с маршрутом из ядра: **92**.
- Удалено: **0**.

## Партитура показа — что перенесено дословно и не сжимается без владельца

| Блок | Файл |
|---|---|
| «Вывод И Стоп» — code-блок из пяти строк + условия готовности | `output-stop.md` |
| «Результат gate» ×7 (decision trace каждого gate) | `gate0-admission.md`, `gate1-chain.md`, `gate2-owner.md`, `gate3-steering.md`, `gate4-control.md`, `gate6-proof.md` (+ хвост Gate 3 в том же файле) |
| Контрастивная демонстрация «Слабо / Сильнее» | `steering-cell.md` |
| Findings Contract (code-блок) + «Готово, когда» | `language-quality-findings.md` |
| «Findings — формат» + «Выход» смыслового аудита | `audit-meaning-criteria.md` |
| «Findings — формат» размещения | `audit-placement-structure.md` |
| «Выход» размещения | `placement-protocol.md` |
| Instruction-Layer Delta packet (question/scope/evidence/verdict/consumer) | `cli-recipes.md` |
| «Stop» модели-дивергенций | `llm-divergences-stop.md` |
| Режимные bullets «Audit/review/diagnose» и «Change/fix» + «Мера продукта» | `product-jobs.md` |
| Decision traces, не длинная анкета | `controller.md` |

## Что изменено помимо переноса

1. Заголовки секций `SKILL.md` подняты с `###`/`##` до `#` при вынесении в
   отдельный файл (форматирование, не смысл).
2. Ссылки `](references/x.md)` → `](x.md)` внутри `references/` (канонизация
   указателя).
3. Два предложения (`Держи компактное рабочее состояние…` и `Каждый gate должен
   породить…`) перенесены из секции `Controller` в ядро дословно и удалены с
   прежнего места — один экземпляр, без дубля.
4. Добавлены только маршрутные строки (метки `нов.` в легенде) и одна строка
   «Читается до Gate 0» / «Открывается из …» в шапках производных файлов.
   Нормативного текста они не содержат.
