# Карта стадий и самостоятельных единиц — финальные байты

Единицей считается каждый отдельно нарушимый predicate, а не строка или пункт.
Уникальный контекст и цели body исключены из счёта только по прямому правилу
`1skill-creation/SKILL.md:68-71`.

| Файл/стадия | Наблюдаемый вход | Выход | Единицы |
| --- | --- | --- | ---: |
| `SKILL.md` / router | Skill выбран по `description`. | Следующая одна stage либо stop. | 20 |
| `owner-protocol.md` | Первый advice/review в task. | Дословные owner methods прочитаны; возврат в body. | 19 |
| `prepare-advisor.md` | Body выбрал нового advisor. | Approved advisor artifact. | 18 |
| `fresh-one-shot.md` | Immutable one-shot envelope; независимой работы нет. | Один raw packet или invocation failure. | 16 |
| `parallel-one-shot.md` | Immutable envelope; полезная независимая работа есть. | Один opaque outcome ref. | 18 |
| `accept-one-shot.md` | Raw one-shot packet. | Validated Opus result или typed failure. | 13 |
| `session-open.md` | Prepared advisor; управление нужно с первого turn. | Один live native ID и initial state. | 14 |
| `session-action.md` | Live Opus ID, state и requested action. | Raw action packet или waiting marker. | 20 |
| `session-observe.md` | Opus ID ждёт status либо content. | Snapshot, terminal result или failure. | 19 |
| `existing-sessions.md` | Явный list/read request. | Один bounded read-only result. | 7 |
| `session-recovery.md` | Exact typed session failure. | Одна action на том же ID либо stop. | 19 |
| `failure-recovery.md` | Exact typed non-session failure. | Одна recovery action либо evidenced stop. | 19 |
| `agents/openai.yaml` | Ручной/implicit launch metadata. | Нейтральный requested route и MCP dependency. | 5 |

## Самостоятельность

- Каждый reference выполняется по body, одному названному файлу и артефактам
  предыдущих стадий; reference не требует чтения другого reference.
- Output каждой стадии возвращается в body: approved advisor artifact, raw
  packet, opaque ref, typed action/state/result либо exact failure.
- Blocking и parallel execution намеренно различны; общий brief и acceptance
  вынесены в отдельные последовательные стадии, поэтому их механика не
  дублируется.
- Session lifecycle разделён по разным моментам решения: открыть identity,
  выполнить action, наблюдать outcome, восстановить failure.

## Проверка удаления

- Без `owner-protocol` теряются буквальные способы владельца.
- Без `prepare-advisor` execution stages снова дублируют prompt/data/tool
  contract и выходят за budget.
- Без отдельного acceptance transport receipt смешивается с Opus result.
- Без session split один файл одновременно требует initialization, state action,
  waiting и recovery и превышает двадцать единиц.
