# Карта рефактора 1claude-mcp — 2026-08-31

Clean-room кандидат: `skills/1claude-mcp/work/refactor-2026-08-31/draft/`.
Старый tracked owner: `experiments/claude-bridge/codex-skill/1claude-mcp/`.

## Сохранено

| Смысл старого пакета | Носитель кандидата |
| --- | --- |
| Opus — независимый советник/reviewer до работы, параллельно и после; Codex владеет проверкой и финальным ответом | Уникальный контекст, цели и one-shot stages |
| Blocking one-shot — default без полезной параллельной работы; yielded route условен | Router, `fresh-one-shot.md`, `parallel-one-shot.md` |
| Session — opt-in только для follow-up/steer/status/stop | `session-open.md`, `session-action.md`, `session-observe.md` |
| Opus-only и fail-closed для fresh, resumed и inspected sessions | Description, owner protocol, acceptance и session gates |
| Goal/Context, максимум десять существенных границ и outcome вместо процедуры | Цель 3, `owner-protocol.md`, `prepare-advisor.md` |
| Clean launch без auto-loaded instruction stack, но с чтением нужных файлов и exact owner named capability | Уникальный контекст и `prepare-advisor.md` |
| `xhigh` default, `max` только для оправданного fresh call | `prepare-advisor.md` |
| Один yielded Promise без polling, duplicate call или transient session | `parallel-one-shot.md` |
| Exact tool, model/session/effort/warnings evidence и локальная проверка claims | `prepare-advisor.md`, `accept-one-shot.md`, Stop |
| Anthropic data boundary и host approval | `prepare-advisor.md` |
| Один native `session_id`, fresh/resume, state-aware action, bounded observe и cleanup | Session stages и recovery |
| Read-only list/read active sessions и запрет resume active owner | `existing-sessions.md` |
| Typed recovery без automatic retry, trust-boundary substitution или ложной атрибуции | Recovery stages |

## Поглощено более сильным контрактом

| Старый носитель | Куда поглощён смысл |
| --- | --- |
| `opus-agent-prompting.md` | Task-scaled deliverable и verification/delegation effort находятся в `prepare-advisor.md`; Goal/Context и непродуцедурность держат цели и owner protocol. |
| `claude-native-tools.md` | Volatile inventory снят; outcome-зависимая capability передаётся exact owner/address, а выбор доступного инструмента оставлен Opus. |
| Развёрнутый список hidden/raw session data | Сжат до typed state, bounded observe и visible conversation; точный public schema остаётся у bridge. |
| Повторяющиеся stop/retry запреты | Stop принадлежит body, а recovery разделена по non-session и session failure. |

## Снято

| Элемент | Причина снятия |
| --- | --- |
| Обязательная XML-форма brief | Владелец требует смысловые Goal/Context, но XML как способ не называл; clean-room дизайн его не вывел. |
| Optional XML tags и запрет пустых секций | Материальные данные уже принадлежат self-contained brief; формат не меняет outcome. |
| Статические советы выбирать `Agent`, `Monitor`, `Workflow`, `SendMessage` | Tool set volatile, а владелец запрещает навязывать Opus процедуру; named capability остаётся task context. |
| Project-specific billing path | Глобальный runtime не зависит от одного repo; bridge остаётся owner typed subscription failure. |
| Обязательная start-телеметрия parallel call | `yield_control`, единый Promise, opaque outcome ref и один terminal notification полностью доказывают route; отдельная start-запись outcome не меняет. |

## Почему оставшиеся инструкции нельзя вывести из intent

- Exact MCP addresses, `profile: opus_advisor`, result fields и
  `claude-opus-5` — runtime selector/evidence.
- `yield_control` + one Promise + one `notify` — host-specific parallel route.
- Native `session_id`, state transitions и active lease conflict — bridge state
  machine.
- Typed recovery и запрет retry/substitution предотвращают повторную трату и
  скрытую смену trust boundary.
- Anthropic dispatch и host approval — внешняя data boundary, которую clean
  launch сам по себе не раскрывает.

## Материальные свойства и falsifiers

| Изменение | Решение/evidence | Property | Falsifier |
| --- | --- | --- | --- |
| XML снят | Owner требует Goal/Context и ≤10 границ: `_ops/chat-recall/2026-08-26-173027-codex-01a03e0c.md:22-23`; clean-room draft не предположил формат. | Brief semantic, не syntax-owned. | Owner выбирает XML как обязательный способ либо probe неоднозначно собирает Goal/Context без него. |
| Static native-tool routing снят | Owner запрещает процедурность: `_ops/chat-recall/2026-08-14-135604-Codex-019ffae9.md:19`; current tool descriptor в `experiments/claude-bridge/src/ask-server.js:140-145` оставляет Opus native tools. | Skill передаёт capability owner, Opus выбирает tool. | Representative task не может получить required named capability по exact owner/address. |
| Prompting reference поглощён | Official owner: <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5>; owner требует следовать Anthropic: `_ops/chat-recall/2026-08-26-173027-codex-01a03e0c.md:22`. | Preparation держит только current Opus deltas. | Official guidance либо representative eval требует отдельного cognitive mode. |
| Runtime разделён на самостоятельные stages | `~/.codex/skills/1skill-creation/SKILL.md:68-73`, `~/.codex/skills/1skill-creation/references/reference-files.md:12-31`; финальная unit-map — `reference-map.md`. | В каждый момент body + один reference с наблюдаемым input/output. | Реальный route требует одновременно читать два references или stage не выпускает адресуемый artifact. |
| Opus/result gate усилен | `experiments/claude-bridge/src/claude-policy.js:11-24`, `experiments/claude-bridge/src/claude-result.js:33-35,75-113`; owner Opus-only: `_ops/chat-recall/2026-08-14-135604-Codex-019ffae9.md:21`. | Fresh и session fail-closed без affirmative Opus evidence. | Bridge schema/model contract меняется либо probe принимает non-Opus как Opus result. |
| Existing-session read отделён от control | `claude_sessions` read-only и `claude_session` stateful: `experiments/claude-bridge/src/ask-server.js:158-225`. | Inspection не приобретает active lease и не создаёт advisor attribution. | Inspection требует mutating session state или split ломает один user-visible operation. |
| Repo billing path снят | Root rule требует project-independent global skill; `experiments/claude-bridge/AGENTS.md` оставляет billing одному owner. | Runtime сообщает typed subscription error без локальной filesystem dependency. | Bridge перестаёт возвращать actionable typed failure и cross-project recovery требует portable details. |
| Unnamed other-model request запускает Opus | Старый trigger и loss-check сохранены в `routing-decision.md:22`; функция требует независимый взгляд другой семьи. | Неназванное семейство получает Opus implementation. | Use probe уходит без second opinion либо конфликтует с явно выбранным другим family skill. |
| Named non-Opus Claude не проходит как advisor | Owner разрешил только Opus: `_ops/chat-recall/2026-08-14-135604-Codex-019ffae9.md:21`; terminal gate проверяет actual model. | Sonnet/Fable route останавливается либо предлагает Opus, но не подменяет attribution. | Near-miss probe принимает non-Opus result как мнение Opus. |
| Session list/read/control входит в trigger | Старый public surface сохранён; `experiments/claude-bridge/src/ask-server.js:158-225` различает stateful и read-only tools. | Запрос к Claude session активирует ровно нужный stage. | Representative list/read/continue phrase пропускает skill или превращает inspection в advice. |
| Blocking и yielded routes условны | Поздняя коррекция владельца: `_ops/chat-recall/2026-08-31-212001-Codex-01a0589c.md:18`. | Без независимой работы Codex blocking ждёт Opus; при ней используется один yielded call. | Probe без полезной работы запускает background protocol либо parallel probe блокирует Codex. |

## Итог

Потерь функции, end state или требуемого владельцем способа нет. Пакет уменьшен
с 301 до 229 строк; пять старых references заменены одиннадцатью короткими
стадиями с отдельными входами и выходами. Объём не был критерием удаления.
