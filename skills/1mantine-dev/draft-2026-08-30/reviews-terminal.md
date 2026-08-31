# Terminal check-approve — exact candidate

## Exact candidate

Package hash: `62167c5a7adacf4b63a0e95c5421519bed4664f930b4e3074ffcc77f85eb2c7f`.

Алгоритм: SHA-256 по отсортированным runtime paths `SKILL.md` и `references/*.md`; для каждого файла хэшируются `relative-path + NUL + bytes + NUL`.

Файловые SHA-256:

- `SKILL.md`: `47adf49dbc5485a49915f848ffb83954ff1647ecf382f00f9cf7d597552a5aae`.
- `references/audit.md`: `2eefeaef760245767f121f435e2850cdfc6841dd4d0347d5d5178099f8cee858`.
- `references/last-year.md`: `097ca476bfd74df4023f63429a49b7b05eb01fb166bdf31a80f6a927099d7ed2`.

## Verdicts

Uncontaminated literal checker `/root/mantine_literal_clean_terminal` вернул пустой список findings.

Exact counts, принятые literal pass: `SKILL.md` 36; `audit.md` 34; `last-year.md` 28; active sets `core` 20, `version-window` 19, `version-confirmation` 11, `audit-scope` 12, `audit-candidates` 19, `audit-decision` 15.

Trajectory checker `/root/mantine_trajectory_terminal` подтвердил version-before-discovery, full public contract, conditional audit и falsifying runtime check.

Trajectory checker оставил один принятый handoff-gap: final confirmation output не говорит буквально, что сохраняет self-contained task packet и resolved cohort.

Trajectory finding о readable/local custom отклонён: эта обязанность остаётся active global goal в `SKILL.md`, а audit decision отдельно применяет aggregate-complexity gate.

Clean executor `/root/mantine_probe_clean_terminal` наблюдаемо прошёл `version-window → confirmation → component discovery → audit-scope → audit-candidates → audit-decision`.

Clean executor выбрал `SimpleGrid`/`Grid` с CSS residue по геометрии, `useField`/`useForm`, notifications, confirm-modal manager и прямой `Button`; проверки без app repo честно вернул как `unknown`.

Clean executor оставил второй принятый handoff-gap: audit input `cohort, scope и текущее решение` не говорит буквально, что scope сохраняет required behaviors из task packet.

## Terminal residue

После двух полных repeats `check-approve.md` требует остановиться и назвать остаток.

Runtime candidate поэтому не изменён после terminal review.

Перед approval/install нужен новый bounded review cycle для двух связанных правок: сохранить self-contained task packet в final version delta и явно передать required behaviors в audit scope.

Официальные Codex и Claude packages не менялись; оба live `SKILL.md` сохранили SHA-256 `91354c6f5ad37ce14b5459e12cbf27d653c01e7b1bea681ab024931ceec8da54`.
