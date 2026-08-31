# Карта рефактора 1claude-mcp — 2026-08-31

Clean-room кандидат: `skills/1claude-mcp/work/refactor-2026-08-31/draft/`.
Старый tracked owner: `experiments/claude-bridge/codex-skill/1claude-mcp/`.

## Сохранено

| Смысл старого пакета | Носитель кандидата |
| --- | --- |
| Opus — независимый советник/reviewer до работы, параллельно и после; Codex владеет проверкой и финальным ответом | Уникальный контекст, цели и one-shot references |
| Один blocking ask — default; session только для follow-up/steer/status/stop | `fresh-one-shot.md`, `parallel-one-shot.md`, `session-control.md` |
| Opus-only и fail-closed для fresh, resumed и inspected sessions | `description`, owner protocol, terminal gates и `existing-sessions.md` |
| Реальный `cwd`, Goal/Context/Task, не больше десяти существенных обязательств, outcome вместо процедуры | Цель 3 и one-shot references |
| Clean launch без auto-loaded instruction stack, но с чтением нужных файлов и exact owner named capability | Уникальный контекст и `fresh-one-shot.md` |
| `xhigh` default, `max` только для оправданного fresh call | `fresh-one-shot.md` |
| Один yielded call без polling, duplicate call или transient session | `parallel-one-shot.md` |
| Exact tool, model/session/effort/warnings evidence и локальная проверка claims | one-shot references и Stop |
| Anthropic data boundary, host approval и subscription-only recovery | `fresh-one-shot.md` и `failure-recovery.md` |
| Один native `session_id`, fresh/resume, bounded observe, state-aware send/steer/stop и cleanup | `session-control.md` |
| Read-only list/read active sessions и запрет resume active owner | `existing-sessions.md` |
| Typed recovery без automatic retry, credential/provider substitution или ложной атрибуции | `failure-recovery.md` |

## Поглощено более сильным контрактом

| Старый носитель | Куда поглощён смысл |
| --- | --- |
| `opus-agent-prompting.md` | Output bounds, scope/stop и запрет generic verifier/fan-out находятся в one-shot; Goal/Context/Task и непродуцедурность держат цели и owner-methods. |
| `claude-native-tools.md` | Volatile inventory снят; outcome-зависимая capability передаётся exact owner/address, а выбор доступного инструмента оставлен Opus. |
| Развёрнутый список hidden/raw session data | Сжат до bounded typed observe и visible conversation; точный public schema остаётся у bridge. |
| Повторяющиеся stop/retry запреты | Один Stop в body и один condition-owned recovery reference. |

## Снято

| Элемент | Причина снятия |
| --- | --- |
| Обязательная XML-форма brief | Владелец требует смысловые Goal/Context, но XML как способ не называл; clean-room дизайн его не вывел. |
| Optional XML tags и запрет пустых секций | Материальные данные уже принадлежат self-contained brief; формат не меняет outcome. |
| Статические советы выбирать `Agent`, `Monitor`, `Workflow`, `SendMessage` | Tool set volatile, а владелец запрещает навязывать Opus процедуру; named capability остаётся task context. |
| Project-specific billing path | Глобальный runtime не зависит от одного repo; bridge остаётся owner typed subscription failure. |

## Почему оставшиеся инструкции нельзя вывести из intent

- `profile: opus_advisor`, exact MCP address, result fields и
  `claude-opus-5` — runtime selector/evidence.
- `yield_control` + one Promise + one `notify` — host-specific parallel route.
- Native `session_id`, state transitions и active lease conflict — bridge state
  machine.
- Typed recovery и запрет retry/credential substitution предотвращают
  повторную трату и скрытую смену trust boundary.
- Anthropic dispatch и host approval — внешняя data boundary, которую clean
  launch сам по себе не раскрывает.

## Материальные свойства и falsifiers

| Изменение | Решение/evidence | Property | Falsifier |
| --- | --- | --- | --- |
| XML снят | Owner требует Goal/Context и ≤10 границ: `_ops/chat-recall/2026-08-26-173027-codex-01a03e0c.md:22-23`; clean-room draft не предположил формат. | Brief semantic, не syntax-owned. | Owner выбирает XML как обязательный способ либо realistic probe неоднозначно собирает Goal/Context без него. |
| Static native-tool routing снят | Owner запрещает процедурность: `_ops/chat-recall/2026-08-14-135604-Codex-019ffae9.md:19`; current tool descriptor в `src/ask-server.js:140-145` оставляет Opus native tools. | Skill передаёт capability owner, Opus выбирает tool. | Representative task не может получить required named capability по exact owner/address. |
| Prompting reference поглощён | Current official owner: <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5>; owner требует следовать Anthropic: `_ops/chat-recall/2026-08-26-173027-codex-01a03e0c.md:22`. | One-shot держит только current Opus deltas. | Official guidance либо representative eval требует отдельного когнитивного режима. |
| Fresh/parallel/session/read/recovery разделены | Public tools имеют разные input/state contracts: `src/ask-server.js:136-225`; `reference-map.md` даёт самостоятельные входы/выходы. | В каждый момент body + один reference. | Реальный маршрут требует одновременно читать два references или не может завершиться по собственному output. |
| Opus/result gate усилен | `src/claude-policy.js:11-24`, `src/claude-result.js:33-35,75-113`; owner Opus-only: `_ops/chat-recall/2026-08-14-135604-Codex-019ffae9.md:21`. | Fresh и session fail-closed без affirmative Opus evidence. | Bridge schema/model contract меняется либо probe принимает non-Opus как Opus result. |
| Existing-session read отделён от control | `claude_sessions` read-only и `claude_session` stateful: `src/ask-server.js:158-225`. | Inspection не приобретает active lease и не создаёт advisor attribution. | Inspection требует mutating session state или split ломает один user-visible operation. |
| Repo billing path снят | Root rule требует project-independent global skill; `experiments/claude-bridge/AGENTS.md` оставляет billing одному owner. | Runtime fail-closed сообщает typed subscription error без локальной filesystem dependency. | Bridge перестаёт возвращать actionable typed failure и cross-project recovery требует portable details. |

## Итог

Потерь функции, end state или требуемого владельцем способа нет. Пакет уменьшен
с 301 до 185 строк; пять старых references заменены пятью самостоятельными
режимами с наблюдаемыми входами и выходами. Объём не был критерием удаления.
