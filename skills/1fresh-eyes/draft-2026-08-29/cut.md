# Cut — draft 2026-08-29

Статус: карта среза для проверки. Не live contract.

## Сохранено

- Телос: лучший следующий ход и альтернатива, а не критика ради критики.
- Decision gate: вопрос на столе, что изменит ответ, конечный результат.
- Панель: `ladder` / `solvent` / `prospector` + cross-family Premortem.
- Named exception: явно выбранный пользователем specialist profile без панели, но с тем же isolation contract.
- Non-leading brief, отдельные evidence paths, source verification и synthesis без голосования.
- Terminal barrier, честный stop и полноценный surviving route.

## Поглощено зонтиками

- «Цель / Критерии / Инварианты / Дельта» → Контекст + три цели пользователя.
- Карта известных сбоев → несколько когнитивных владельцев; reference читается только когда его локальная механика реально нужна.
- Gate, isolation, launch, evidence judgment и handback → body + `packet/panel/named/synthesis/steering`.
- Детальная шестиуровневая taxonomy → четыре action labels в `synthesis.md`; native disagreement и source verification сохранены.
- Send/resume/follow-up matrix → короткий runtime `steering.md`.

## Перемещено

- Packet construction отделён от launch; frozen packet — единственный обязательный промежуточный артефакт.
- Cross-family Premortem обеих сред остаётся отдельным self-contained `premortem.md` и выполняется из frozen packet до native launch; native reports в него не входят.
- Claude `premortem.md` использует `$1codex`, Codex `premortem.md` — `$1claude-mcp`; call mechanics и retained correction принадлежат этим runtime-owner-ам.
- Runtime drift/date hypothesis → `refactor-map.md` как validation note, не постоянное behavioral rule.
- Полный inventory и причины каждого среза → `refactor-map.md`.

## Удалено из candidate

- Auditor/md-scout-specific classification из panel synthesis; их native products сохранены одной строкой.
- Примеры domain critics из panel brief: fixed panel уже разведена direction-контрактами ролей.
- Автоматический rerun при одинаковом выводе: failure теперь одинаковые method/evidence/consequence, а не честный consensus.
- Повторное объяснение, что критики и evidence-products не являются panel lenses.
- Недостижимые panel-вердикты `satisfied` / `architecture_ok`.
- 19–23 micro-stages, появившиеся из буквального превращения числа 20 в цель.
- Пустой reference для named handback: return без смены формы остаётся body-only действием.
- Human-history `cut.md` из installed Claude package: история остаётся только в repo.

## Не принято

- Panel-only scope: фальсифицирован отсутствием второго owner-а isolation для named roles и прямым owner-решением про named exception.
- Dynamic roster или optional Premortem: внешние прецеденты и Solvent дали гипотезу, но буквальное owner-решение фиксирует четвёрку; A/B нет.
- Перенос non-leading rules в шесть agent definitions: дублирует instruction budget и слабее caller-side gate.
- Новый shared owner: runtime-формы различаются cross-family и launch-механикой, поэтому сохраняются два tracked runtime owner-а, а portable-дерево не изобретается.

## Размер и внимание

- Body обеих сред после bounded-pass содержит шесть шагов вместо десяти.
- Named, packet, panel и synthesis потеряли только строки, уже вытекающие из усиленных `Уникального контекста` и `Цели пользователя`.
- Premortem и steering почти не сжаты: они держат невыводимые runtime interfaces, recursive guard, retained route и falsifying stop.
- Финальный atomic ledger хранится в install evidence; excess остаётся risk note, не повод снова дробить bridge.
