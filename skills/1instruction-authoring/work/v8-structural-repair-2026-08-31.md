# V8 — структурная коррекция

## Основание

- Owner correction:
  `_ops/chat-recall/2026-08-31-121641-Codex-01a04dbd.md:16`.
- Действующий маршрут: поздняя правка, потерявшая требуемый способ или порядок,
  возвращается к `1skill-creation/references/behavior-protocol.md`, а не
  перезапускает clean-room.
- P-002/P-003 требуют сохранить автономный commander's intent; P-004/P-005 —
  наблюдаемую проверку; GOAL запрещает рост instruction-процесса.

## Fresh Eyes

- Premortem: косметическое переименование без причинного порядка повторит
  провал; новый файл или стадия будут ранним сигналом переусложнения.
- Ladder: вернуться к самой ранней затронутой стадии и не переносить v7 approval
  на новые байты.
- Solvent: не повторять clean-room и checker-волны; смешение verification и
  install размывает самостоятельность reference.
- Prospector: prior art сохраняет общий критический порядок в entrypoint, а
  условную тяжёлую стадию делает прямо маршрутизируемой и самодостаточной.

## Решение

Создать отдельную четырёхфайловую v8. В `SKILL.md` поставить после Уникального
контекста и Цели пользователя главный причинный `Протокол поведения`.
`verification.md` оставить одной самостоятельной стадией с явными входом и
выходом. Terminal write сохранить последним условным шагом основного протокола.
Tracked owner, projections и live не менять до безусловного approval точных
байтов v8.

Фальсификатор: чистое чтение тела не позволяет выполнить обычный authoring без
reference, reference нельзя выполнить по телу, кандидату и текущему пути либо
дельта меняет функцию, commander's intent или clean-scout boundary.

## Карта сохранения

| Свойство v7 | Адрес v8 | Вердикт |
| --- | --- | --- |
| Внешняя правда достигает первого зависимого решения | `SKILL.md:8-18,25-40` | Сохранено и превращено в причинный порядок. |
| `no-change` требует наблюдаемого пути | `SKILL.md:27-29` | Сохранено. |
| Неизвестное ребро исследует чистый scout | `SKILL.md:30-32`; `agents/zone-scout.md` | Сохранено; agent bytes не менялись. |
| Один владелец и самый узкий слой | `SKILL.md:33-37` | Сохранено. |
| Только невыводимые hard lines | `SKILL.md:38-40` | Сохранено. |
| Causal proof exact candidate | `references/verification.md:12-31` | Сохранено в самостоятельной стадии. |
| Exact authority и owner-first parity | `SKILL.md:43-47` | Перенесено из reference в terminal step основного протокола. |
| Runtime metadata | `platforms/codex/agents/openai.yaml` | Сохранено без изменения байтов. |

Потерь функции, commander's intent, clean-scout boundary и terminal write не
обнаружено. Удалена только смешанная ownership двух стадий внутри
`verification.md`; install-обязательства не вырезаны, а перенесены в тело.

## Активные наборы

Единица — независимо нарушимый смысл; завершённые стадии представлены их
артефактами, а не продолжают действовать полным протоколом.

| Режим | Единицы | Основание |
| --- | ---: | --- |
| Обычный authoring | 16 | Главная цель, текущий причинный шаг и ещё действующие hard lines. |
| Clean scout | 15 | Неизменённый самостоятельный agent contract v7. |
| Verification | 20 | 3 persistent root units + 17 units reference. |
| Install continuation | 13 | Identity, exact authority, owner-first write, existing surfaces и parity. |
| Codex invocation | 1 | `default_prompt` только вызывает скилл. |

Reference-17: вход 3; terminal output 2; identity 2; active budget 2; matched
trial 4; observable verdict 4. Уникальный контекст и поясняющая часть цели не
добавляют независимого выбора к этим единицам.

## Причинно затронутое evidence

1. `main protocol in body`: falsifier — без reference нельзя получить полный
   кандидат. Direct trace v8: карта → наблюдаемый gap/no-change → evidenced
   owner edge → placement → commander intent → candidate → verification
   receipt → install/no-write.
2. `reference is one independent stage`: falsifier — стадия требует approval,
   installation state либо другой reference. В v8 её вход — candidate, root
   goal и current path; выход — один causal receipt; ссылок на другие файлы нет.
3. `terminal write preserved`: falsifier — разрешена установка другого hash,
   отсутствующего owner либо новых projections. Шаг 8 требует один identifier,
   существующего owner, существующих surfaces и terminal parity.

Прежний long-trajectory probe сохраняется только для незатронутого свойства
доставки внешней правды. Он не доказывает вероятность соблюдения нового
порядка; две reviewer-волны задачи уже исчерпаны, поэтому новые checker-ы не
вызывались. Остаточный риск — adherence нового порядка вне прямой структурной
трассировки.

## Exact checks

- Candidate files: 4.
- Full fingerprint: `b20d1af62aa61fb0f8f90dd9b7f6ba9d7f9ae48731eaa5a57e8fa276cf5835a0`.
- Portable fingerprint: `f4effccf2be41e2c73e81a192d3fded760d02d603a354b3002eefbc48cd01774`.
- `quick_validate.py`: pass.
- `qv-skill`: pass.
- `md check`: 3 Markdown targets, 0 issues.
- `git diff --check`: pass.
- V7, shared owner, tracked projections и live остались на fingerprint
  `b6dd5b397cc78d49b6edd7212a48bb021a7c6b41b6feec359b81aaeaf378b1ee`
  для полного Codex-пакета и `db9c08c2fe044c05d8b3718e9f674c590b2daebab1dbc88efa7ad09b068538e7`
  для portable Claude-пакета.

Статус: exact v8 candidate готов к owner review, не записан в tracked owner и
не установлен. Любая следующая правка создаёт новый identifier.
