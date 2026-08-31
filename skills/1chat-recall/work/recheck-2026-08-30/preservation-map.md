# Карта сохранения функции

| Invariant | Current surface | Evidence |
| --- | --- | --- |
| topic map читается до Capture | Capture шаг 3 | clean Capture PASS; missing map → gap |
| новая topic boundary создаётся только после полного сравнения | Capture шаг 3; helper transaction | new-topic add/rollback tests |
| session-context — полный актуальный индекс разговора | body context; Capture шаг 2/4 | update + session-card retrieval tests |
| context-note — короткий keyword index цитаты | body context; Capture context | quote-card search/show tests |
| topic description — отдельный route, не evidence | Retrieval шаг 2; `topic_candidates` | topic-only/both/retired route tests |
| выбранный session holder читается целиком | Retrieval context/step 3 | explicit runtime contract anchor |
| важная тема допускает один неблокирующий фоновый поиск | Retrieval шаг 4 | exact prose anchor; не запускается в repair task |
| cancellation/conflict stays linked | Capture step 3 (`--supersedes` / `--contested`) | helper anchor validation tests |
| retrieved quote is dateable | Retrieval cards/records and human rendering include `date` + relative `age`; `--timeline` keeps chronology | date/age conflict suite + clean corpus probe |
| newer direct same-scope position wins | explicit verified `supersedes` hides the cancelled record from decision-scoped query | old/new query vs timeline probe |
| invalid supersedes cannot rewrite scope/time | helper requires equal topic and strictly newer timestamp; failed links remain diagnostic/contested | scope/order characterization test |
| unresolved/undatable/non-owner evidence cannot become position | decision query filters `contested`, unknown timestamp, `note` and `raw`; timeline remains diagnostic | exclusion characterization test |
| agent carrier не owner authorship | body context; Capture шаг 1; Integrity шаг 2 | tool-sent probe: zero holders |
| search output не current truth | Retrieval context/steps 2–3 | literal evidence + live owner/`abstain` |
| semantic и offline routes | Retrieval steps 1–2 | hybrid diagnostic → one prepare → lexical PASS |
| Repair не создаёт второй writer | Integrity шаг 3 → router → Capture | native coordinates preserved |
| transcript link не становится corpus field | Capture шаг 3 | source address только в transition packet |
| mutation не портит source | Integrity шаг 4 | explicit owner request + backup/validation |

Три references имеют разные terminal outcomes; topic-route и Recovery остаются
ветвями Retrieval, не отдельными стадиями или derived topic layer.
