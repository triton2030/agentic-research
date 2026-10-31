# Обновление инструментов — 2026-10-31

Заказ владельца: «Да, обновить» — починить `token-counter` и обновить
устаревшие инструменты. Затем правка скила по замерам после обновления
(`upgrade.diff`).

## Сделано

- `brew upgrade --formula`: 23 формулы, среди них DuckDB 1.5.6 → 2.0.0,
  Node 26.13.0, Python 3.15.2, uv 0.13.6, gh 2.103.3, pnpm 12.16.1, Mole 1.66.
  Лог — `/tmp/brew-upgrade-2026-10-31.log`. Casks (Obsidian, Raycast,
  LibreOffice, Rive) не трогались: это приложения, не CLI.
- `brew upgrade node` перезаписал `/opt/homebrew/bin/npm` комплектным 11.20.0
  (лог: `These files were overwritten during the brew link step`) →
  `npm install -g npm@12.2.1`.
- npm global: agent-browser 0.41.0, vercel 65.9.0, eslint, knip, redocly,
  firecrawl-cli, typescript-eslint. npm 12 заблокировал скрипты
  agent-browser, esbuild, koffi, fsevents; `vercel whoami` и
  `agent-browser --version` работают, скрипты не разрешались.
- `token-counter`: `uv tool install token-counter-cli --reinstall --with 'idna>=3.15'`
  → `token-counter --help` работает. `uv tool upgrade --all`: ruff 0.17.3,
  rumdl 0.3.2 и др.
- Не обновлён `graphify`: точный pin `graphifyy[sql]==0.9.73` поставлен
  при подключении Graphify к MAVO (индекс, Git-хуки; сессии mavo3
  `bbe9dc51`, `f82948ba`).
- Не обновлён `~/.local/bin/node` → `~/.local/share/node/v26.12.1`:
  подписанная универсальная сборка nodejs.org, не Homebrew; кто и зачем
  поставил 2026-10-21 — не найдено.

## Замеры для правки скила

| Утверждение | Команда → результат |
|---|---|
| DuckDB 2.0 агент-режим | `duckdb -c "select * from range(1500)"` → Markdown, `first 20 and last 20 of 1500 rows (.maxrows -1 for all)`; баннер `duckdb agent mode on` — в stderr |
| ячейка обрезается | `select repeat('x',2000)` → строка вывода 521 байт |
| `-csv` даёт всё | `duckdb -csv … range(1500) \| wc -l` → 1501 |
| `~` частичное | `select 'abc' ~ 'b'` → true |
| `~/.local/bin/node` не обновился | `node --version` 26.12.1, `/opt/homebrew/bin/node` 26.13.0 |

## Решения по тройке

- DuckDB: «первые и последние 20 строк» заменено правилом из `.help agent`
  (целиком до 1000 строк и 10 000 байт; ячейка 500; ошибки JSON в stderr).
- `graphify`: причина pin (MAVO) из скила снята — в `mavo3` файлов
  `.graphifyrc`/`.graphifyignore` сейчас нет, связь не подтверждена; оставлен
  факт `==0.9.73` и запрет снимать без владельца.
- `~/.local/bin/node`: добавлено «кто поставил — не записано, без владельца
  не меняй» — иначе агент применит к нему правило о совместном обновлении.
