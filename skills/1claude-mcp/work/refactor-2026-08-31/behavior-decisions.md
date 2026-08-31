# Допуск поведения сверх commander's intent

## Пустой протокол для выводимого поведения

Из Уникального контекста и целей уже выводятся роль советника/reviewer,
временные маршруты до/параллельно/после работы, верхнеуровневые цель и контекст
brief, непродуцедурность, локальная проверка и владение Codex финальным ответом.
Отдельные инструкции для этого поведения не допускаются.

## Требуемые владельцем способы — дословно

> Мы не меняем предыдущую цель клода быть советником или ревьюером Проверь важно чтобы он имел права на чтение других файлов тоже и проверь чтобы мы писали ему промпты по лучшим практикам самого антропик, мы не должны ограничивать модель процедурностю и писать ему вопросы отталкиваясь от цели и проблемы и не говорить ему как ему надо думать и что делать

> Плюс клода можно использовать не только как ревью работы но также и перед работой фоном, пока ты работаешь и уже начал работу, чтобы клод паралельно работал и дал потом свой совет как бы он приступил к задаче

> Надо запретить использовать фейбл, только опус

> Но еще, я думаю, в самом скилле надо сказать, что задачи надо описывать подробно и как промты, то есть описывать цель и контекст. Обязательно, чтобы эти разделы присутствовали в промте, и именно цель верхнеуровневая. И мы по лучшим практикам, которые сейчас ты должен изучить в интернете по документации клода и опуса, должны писать промты ему так, как они говорят. Хотя, по сути, это у нас уже есть вроде бы в этом скиле, но надо проверить.

> И тоже правило такое не больше десяти инструкций или ограничений должно быть. Это означает, что надо выбирать самые важные ограничения, инструкции или границы.

Источники: `_ops/chat-recall/2026-08-14-135604-Codex-019ffae9.md:19-21`
и `_ops/chat-recall/2026-08-26-173027-codex-01a03e0c.md:22-23`.

## Принятые runtime-инструкции — TWI Job Instruction

### 1. Fresh one-shot

- **Подготовка:** готовый brief и реальный project/worktree `cwd`.
- **Действие:** вызвать `mcp__claude_mcp__claude_ask` с
  `profile: opus_advisor`, без `session_id`; `xhigh` остаётся default, `max`
  выбирается только для свежего вызова, когда цена решения оправдывает его.
- **Ключевой момент:** clean launch обеспечивает bridge; prompt просит
  исследовать, не изменяя состояние, но не запрещает читать релевантные файлы.
  Named custom skill, MCP или capability не загружается автоматически: если от
  неё зависит outcome, её exact owner/address входит в `Context`.
- **Ключевой момент prompting:** когда это материально, brief явно калибрует
  visible length, progress cadence, deliverable size, narrow scope и stop; не
  добавляет generic double-check, verifier-subagent или automatic fan-out.
- **Проверка:** `structuredContent` содержит непустой `text`, native
  `session_id`, `requested_model: opus`, `requested_effort` и
  `resolved_model`, начинающийся с `claude-opus-5`.

Исправляемый дефолт — полагаться на prose «используй Opus» или вручную
эмулировать clean environment. Без правки возможны неверная модель и ложная
изоляция. След нельзя подделать пересказом: фактический terminal packet tool-а.

### 1a. External-data boundary

- **Подготовка:** известен brief и материалы, которые Opus может прочитать.
- **Действие:** до dispatch следовать host approval и не расширять разрешённый
  data scope.
- **Ключевой момент:** `claude_ask` отправляет Anthropic prompt и прочитанные
  материалы; clean launch не означает локальный sandbox.
- **Проверка:** observable host approval либо отсутствие dispatch; при отказе
  названо, что не было отправлено.

Исправляемый дефолт — принять clean launch за отсутствие внешней передачи.
Вред — отправка данных вне разрешённого scope. След — host approval/dispatch,
который невозможно заменить пересказом правила.

### 2. Параллельный one-shot

- **Подготовка:** после запуска остаётся полезная независимая работа Codex.
- **Действие:** запустить Promise ровно одного `claude_ask` в одной
  `functions.exec` cell, вызвать `yield_control()`, затем дождаться того же
  Promise внутри cell.
- **Ключевой момент:** не открывать transient session ради одного фонового
  ответа, не polling-овать и не запускать второй вызов; возвращённый packet
  сохранить под task-scoped opaque reference и разбудить root одним `notify`.
- **Проверка:** одна start-запись, один returned packet либо один diagnostic
  отказа и ровно одно terminal notification.

Исправляемый дефолт — сделать blocking wait или построить session lifecycle для
одного ответа. Без правки теряется параллельность либо появляется лишняя
оркестрация. След — наблюдаемая пара start/terminal одной cell и один result ref.

### 3. Terminal acceptance

- **Подготовка:** returned result fresh ask либо terminal session observation.
- **Действие:** прочитать model/effort/warnings/session metadata и только затем
  применять `text` или bounded conversation.
- **Ключевой момент:** tool receipt, progress, `possibly_stalled`, accepted
  command или не-Opus model evidence не являются завершённым мнением.
- **Проверка:** terminal `structuredContent` либо `terminal.kind: success` с
  `resolved_model` Opus; локальные claims проверены отдельным task evidence.

Исправляемый дефолт — принять успешный transport или совет за доказательство.
Без правки Codex объявит review, которого не было. След — сам packet и адреса
локальной проверки.

### 4. Session control

- **Подготовка:** follow-up, steer, status/liveness или stop действительно
  нужны; native `session_id` и `cwd` известны.
- **Действие:** `claude_session open_fresh` начинает новый advisor;
  `open_resume` продолжает известный native ID после исчезновения lease;
  `send` применяется в `idle`, `steer` — в активном состоянии, `stop` закрывает
  lease. `claude_observe` делает один bounded pull или один long-poll.
- **Ключевой момент:** один native ID остаётся единственным адресом; active
  session, найденную через `claude_sessions`, нельзя одновременно открывать
  через `open_resume`.
- **Проверка:** возвращены тот же `session_id`, `accepted_op`, `state`, `cursor`
  и terminal metadata; после stop состояние закрыто или очистка наблюдаема.

Исправляемый дефолт — создать второй handle, polling loop или параллельного
владельца одной conversation. Вред — раздвоение истории, потеря turns и висящий
process. След — typed observation exact native ID.

### 5. Existing sessions и recovery

- **Подготовка:** владелец явно просит список/чтение активной Claude session
  либо точный typed failure уже получен.
- **Действие:** `claude_sessions list_active/read` остаётся read-only; recovery
  выбирается по фактическому error code. Автоматически не повторять
  token-consuming или session-appending вызов; не менять subscription route,
  credentials, model alias и не использовать Fable fallback.
- **Ключевой момент:** resume допустим только с известными native ID, `cwd` и
  новым prompt; unsupported profile/model и отсутствие terminal answer закрывают
  вызов неуспехом.
- **Проверка:** typed error/result сохраняет exact code или model evidence и
  ровно одно названное следующее действие; read возвращает только bounded
  visible user/assistant messages.

Исправляемый дефолт — «попробовать ещё раз» или подменить отсутствующее мнение
своим. Вред — повторная трата, испорченная session и ложная атрибуция. След —
typed error/result и отсутствие второго незапрошенного вызова.

## Решения допуска

- Пять runtime-инструкций приняты: их точные tool/state semantics не выводятся
  из commander's intent и наблюдаемы через callable schema и typed result.
- XML как форма brief снят: владелец требует смысловые секции, но не XML.
- Каталог Claude native tools, role/rubric и обязательный subagent сняты:
  intent и актуальная официальная страница Opus 5 их не требуют; explicit
  generic verifier/fan-out остаётся запрещённым по текущему official owner.
- Billing prose не входит в обычный путь; единственный owner остаётся
  `experiments/claude-bridge/docs/subscription-billing.md`.
