# IL-probes — прогон 1 (кандидат IL-cand-2)

## P1

Правило в `AGENTS.md` не пишется. Первый ход — открыть
`references/product-jobs.md` и `references/controller.md`: `SKILL.md` требует оба
до Gate 0. Сразу за ними открывается `references/gate0-admission.md`, и до его
результата (`mode + one-off|durable + premise status + failed jobs`) никакой
текст правила не формулируется.

## P2

Запрос разбирается на две разные работы, а не исполняется целиком. Первый
наблюдаемый ход — назвать границу и отдать «разнеси на файлы по зонам»
(split/new instruction container) скилу `1ia-audit`, оставив себе только repair
правила про тесты; Gate 2 п.6 прямо требует остановиться до edits, когда нужен
новый контейнер.

## P3

Draft и chain map не правятся на месте. Первый ход — clean re-anchor по
`controller.md`: агент явно отбрасывает draft и все выводы, зависевшие от
опровергнутого owner-а, и заново собирает компактное состояние из подтверждённых
owner facts — то есть перезапускает Gate 1/Gate 2 на импортируемом `AGENTS.md`
как реальном owner-е.

## P4

Строчка в корень сразу не вписывается. Первый наблюдаемый ход — результат Gate 0:
mode `change`, durable-правило, названное основание (stable local fact или
recurring correction) и статус material premise «корень — верный owner». Запрет
владельца на процедуру принимается как форма (Gate 4 п.5: outcome-rule вместо
procedure), но не отменяет chain/owner-проверку до wording.

## P5

Предложенный текст не принимается и не полируется. Первый ход — открыть
`references/gate3-steering.md` и `references/steering-cell.md` и построить cell:
назвать fork (момент, где отчёт начинает писаться), естественный первый акт и
целевой первый наблюдаемый акт. «Будь внимателен» опознаётся как лозунг, `MUST`
на preference — как risk-word overclaim.

## P6

Правило не кладётся в корневой `AGENTS.md`. Первый ход — из Gate 2 открыть
`references/triggered-rules.md` и разместить его как отдельный RULE в
project-owned cold-директории (`_ops/rules/**`), оставив в корне только строку
`observable trigger → exact RULE`; сам RULE несёт `read-when`, target act, owner
и stop.

## P7

Edit не первый. Первый наблюдаемый ход — Gate 6: агент называет самый
правдоподобный bypass (выполнить форму, сохранив старое решение) и строит
различающий probe с заранее объявленными expected old/new first act. Только
после этого — scoped edit в change mode и проверка direct read/diff.

## P8

Первый ход — открыть `references/output-stop.md` и ответить его пятистрочным
блоком: `Mode + durability / Effective chain + owner / Steering fork / Control +
repair / Behavioral proof + risk`. Находки отдаются как exact proposed delta без
edits; если behavioral run не делался, gap называется прямо.

## P9

Файл не пишется с чистого листа и не по шаблону. Первый ход — evidence-база из
`meaning-design-mode.md`: прочитать родительский/корневой `AGENTS.md` и то, что
реально живёт в `_ops/experiments/` («новая зона — читать нечего» не
принимается). Параллельно отмечается, что создание нового instruction-контейнера
может принадлежать `1ia-audit`.

## P10

Дубль не удаляется по факту совпадения. Первый ход — прямое чтение обоих тел
(`src/AGENTS.md` и корневой `AGENTS.md`) и вердикт из трёх: одинаковый смысл →
один owner + pointer, расхождение → drift, другой момент работы → осознанная
свежесть при одном owner-е.

## P11

Ответа «да, много» из общего знания не будет. Первый ход — открыть
`references/claude-discovery.md` → `claude-discovery-placement.md` и назвать
target surface: для Claude Code listing порог сокращения ~1,536 символов, для
portable Agent Skills — 1,024. Выдуманный механизм провала («скил не найдётся»)
явно не приписывается; дизайн триггеров уходит к `1skill-architect`.

## P12

Формулировка не усиливается и не переписывается первым делом. Первый ход — Gate
4 п.1–2: назвать несоответствие control-а — это hard invariant на prose-only
контроле, `NEVER` без runtime-обеспечения есть risk-word overclaim. Repair —
`handoff to enforcement`: permission или `PreToolUse` hook у live runtime
owner-а, инструкция оставляет только route и объяснение.

## P13

В глобальный скил ничего не вписывается. Первый ход — отказ от обобщения на
семью моделей по одному trace (`llm-divergences-stop.md`: «do not infer a
family-wide trait from one trace») и запись наблюдаемого: exact instruction,
tell, реально разрешённые runtime/model. Далее — минимальная wording-дельта на
наблюдаемый gap («when, why, which surface»), а повторяемая находка поднимается
к текущему model owner, не в глобальный reference.

## P14

Первый проект: owner не выбирается из воображаемой chain — первый ход открыть
`references/claude-discovery.md` и проверить load moment `.claude/rules/*.md`
(есть ли `paths`, попадает ли задача под них), при недоступности live-проверки
(`/memory`) назвать gap и остановить repair. Второй проект: этот reference не
открывается вообще — Gate 1 закрывается прямым evidence, повторная верификация
пропускается как уже подтверждённый результат gate.
