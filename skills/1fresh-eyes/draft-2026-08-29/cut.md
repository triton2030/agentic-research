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
- Карта известных сбоев → условия чтения одного reference на каждой стадии.
- Gate, состав, isolation, classification и synthesis → последовательные стадии с одним наблюдаемым выходом каждая.
- `accepted/rejected/deferred/...`, evidence bar и disagreement rules → отдельный `classification.md`; решение → короткий `synthesis.md`.
- Send/resume/follow-up matrix → короткий runtime `steering.md`.

## Перемещено

- Panel и named packet construction отделены от launch; frozen packet — наблюдаемый промежуточный артефакт.
- Codex cross-family prompt остаётся отдельным self-contained `premortem.md` и выполняется из frozen packet до native launch; native reports в него не входят.
- Codex `premortem.md` напрямую владеет одним `claude_ask`; `$1claude-mcp` больше не является вторым procedural owner этой стадии.
- Runtime drift/date hypothesis → `refactor-map.md` как validation note, не постоянное behavioral rule.
- Полный inventory и причины каждого среза → `refactor-map.md`.

## Удалено из candidate

- Auditor/md-scout-specific classification из panel synthesis; их native products сохранены одной строкой.
- Примеры domain critics из panel brief: fixed panel уже разведена direction-контрактами ролей.
- Автоматический rerun при одинаковом выводе: failure теперь одинаковые method/evidence/consequence, а не честный consensus.
- Повторное объяснение, что критики и evidence-products не являются panel lenses.
- Недостижимые panel-вердикты `satisfied` / `architecture_ok`.
- Human-history `cut.md` из installed Claude package: история остаётся только в repo.

## Не принято

- Panel-only scope: фальсифицирован отсутствием второго owner-а isolation для named roles и прямым owner-решением про named exception.
- Dynamic roster или optional Premortem: внешние прецеденты и Solvent дали гипотезу, но буквальное owner-решение фиксирует четвёрку; A/B нет.
- Перенос non-leading rules в шесть agent definitions: дублирует instruction budget и слабее caller-side gate.
- Новый shared owner: текущая owner-топология асимметрична; refactor не изобретает второй source tree.

## Размер и внимание

- Claude/Codex body: 117/107-ish current lines → 38/39 draft lines.
- Claude references: 183 current lines → 116 draft lines в восьми самостоятельных стадиях.
- Codex references: 242 current lines → 133 draft lines в девяти самостоятельных стадиях.
- Первые две оценки active set отозваны; после artifact-stage split предварительный максимум 18, final ledger проверяется с нуля.
