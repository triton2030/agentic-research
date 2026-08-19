# Вырезано — 1cli-tools

## Переработка 2026-08-19

| Было | Решение | Причина |
|---|---|---|
| цель «найти уже установленный инструмент» | снята | владелец исправил назначение: продукт скила — неизвестные модели новые возможности |
| список `rg`, `fd`, `jq`, `ffmpeg`, linters и scanners в теле | снят | обычный inventory не меняет решение современной модели |
| `references/tool-map.md` как общий каталог | снят | один файл смешивал много моментов и в основном повторял известное |
| route `selected TOOL @ PATH → avoided work` | заменён | новый выход фиксирует capability и изменившееся действие |
| generic runtime/machine audit | снят | не новая capability; оставлен только момент version conflict/update |
| общий security scanner SOP | снят | поведенческая инструкция, не доказанная дельта памяти модели |
| `probe-tools.sh` | снят | `which -a`, `command -v`, `realpath` и `--version` уже дают этот минимальный probe |

Не включены `fd`, обычные `jq`/ripgrep flags, LibreOffice, линтеры, test runners,
Biome и стандартные scanner-команды: наличие в help не доказывает дельту памяти
модели. У FFmpeg оставлены только возможности именно active local build.

Из прежнего runtime owner сняты machine-wide process/app/credential layers,
side-effect ledger, blocker ledger и service-mutation guard: они не являются
новыми возможностями CLI. Из security owner сняты scanner choice, execution,
native-binary proof, credential remediation и stop contract по той же причине.

Не создавался полный changelog. В references вошли возможности, которые на этом
Mac отменяют helper, открывают новый route или меняют смысл успешного install.
