# Preservation map — 1fresh-eyes — candidate 2026-08-30

## Вердикт проверки потерь

Первый runtime candidate побайтно совпал с official owners, поэтому старый
behavior surface использован как контроль потерь, а не как форма будущего.
Первый независимый review показал четыре узких terminal/routing seam; current
candidate добавляет их без смены панели, named handback или синтеза.

## Сохранено

| Смысл | Текущий владелец в candidate | Доказательство |
|---|---|---|
| Материальная развилка длинной работы | English `description` + цель | FE-2; trigger probes round 2 |
| Четыре направления | цель + `panel.md` + `premortem.md` | FE-7; panel trial |
| Явно named role без панели | цель + inline named branch | FE-4; named trial round 2 |
| Ненаводящий source-bound packet | `packet.md` goal | clean packet probe 9/9 |
| Frozen-before-report порядок | `packet.md` hard line | isolation failure model |
| Cross-family Premortem | runtime `premortem.md` | FE-7; live Claude session receipt |
| Native reports не видят Premortem | `panel.md` goal | panel trace |
| Отсутствующая named-роль или source path не подменяется | `packet.md` blocker | checker finding + terminal semantics |
| Ошибка premise или missing required check чинится в том же voice | body + `steering.md` | retained correction trace + missing-falsifier trial |
| Новый correction-поток получает полный packet | `steering.md` | clean isolation boundary |
| Невозможная correction типизирована и не протекает в synthesis | global terminal rule + `steering.md` | final trajectory finding |
| Premortem остаётся одной четвёртой линзой | `premortem.md` no-delegation seam | clean-run session `e1057e0b-…` |
| Source verification | `synthesis.md` hard line | decision-changing evidence gate |
| Native disagreement и no vote | цель + `synthesis.md` goal | FE-1; panel synthesis trace |
| `next` / alternative / `unchanged` | цель + `synthesis.md` schema | owner telos; clean run |
| Непроверенный claim или collision останавливает handback | `synthesis.md` | independent trajectory review |
| Не final acceptance | `synthesis.md` hard line | authority boundary |

## Поглощено commander's intent

- Запрет передавать rationale, diagnosis и desired verdict выводится из цели
  neutral packet; clean probe сохранил точные поля без их повторного списка.
- Запрет утечки Premortem в native reports выводится из `panel.md` goal.
- Failure chain, signal, state и priced guardrail выводятся из локальных
  контекста и цели `premortem.md`.
- No-new-voice и steering trace выводятся из `steering.md` goal.
- Native record и разные evidence paths выводятся из `synthesis.md` goal.

## Hard lines, которые нельзя безопасно вывести

- Exact runtime launch (`Agent` non-fork / `fork_turns: none`).
- Exact cross-family owner (`$1codex` / `$1claude-mcp`) и recursion guard.
- Freeze до первого report и bounded waves при capacity.
- First-line Premortem schema и terminal blockers.
- Retained-session correction API и условия нового потока.
- Source verification, terminal gaps/collisions и exact owner handback schema.

Каждая линия имеет закрытую цепочку в `authoring.md`; её снятие вновь открывает
наблюдавшийся failure либо ломает невыводимый runtime interface, terminal edge
или falsifying acceptance.

## Снято или не принято

- Literal demand разных verdicts: одинаковый verdict допустим только у
  материально разных native reports и evidence paths, чтобы сохранить FE-1,
  не заставляя честный consensus изображать конфликт.
- Clean-room `lane-contracts.md`: методы ролей уже имеют owners.
- Clean-room outer envelope и confidence/completeness поля: не требуются
  owner-ом; native output + synthesis goal уже меняют нужное решение.
- Микростадии ради числа 20: увеличивают церемонию без наблюдаемой функции.

## Материальная дельта

- Product Frame: current semantics, cross-runtime symmetry, explicit Fresh
  Eyes trigger и граница одинакового итога.
- Runtime: source-path stop, unavailable named blocker, wrong-premise/missing
  check correction с full-packet restart, global terminal rule, synthesis
  gaps/collisions и no-delegation Premortem. Runtime-цитаты, `Кругов пройдено`,
  повтор terminal routing, форматное дробление tool calls и `named.md` сняты
  после прямого owner-критерия простоты.
- Root/reference descriptions и metadata сохраняют trigger-only форму;
  steering description покрывает wrong premise/missing check, а synthesis —
  наблюдаемый terminal input.
