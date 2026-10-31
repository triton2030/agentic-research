# Освежение 1cli-tools — 2026-10-31

Вход проверки и запись решений этой правки.

## Граница заказа

Адресная правка существующего скила по словам владельца в сессии
`da5e2ae1-9bfe-44c6-89c0-3ad10bc1e3eb`:

1. «вот этот скил стоит обновить, посмотреть всё ли свежее и есть ли что то
   новое чего агенты скорее всего не знают».
2. «этот скилл должен быть короткий, только самым важным, интересным. Всякие
   предупреждения, о которых агенты не знают. Но если что-то можно достать,
   набрав команду помощи или посмотреть в интернете, лучше давать ссылки».
3. «скажем прямо в самом скилле, чтобы если агент вдруг нашел какие-то ошибки
   с инструментами, или что-то обновил, или сам по мере работы разные агенты,
   когда будут находить что-то, чтобы они предлагали исправить скилл. Чтобы
   этот скилл был живой, эволюционирующий».

Класс скила — знание в момент (`origin.md`). Назначение, триггер и форма
«тело короткое, references по моментам» сохраняются.

Строка «Codex» в перечне (`experiments/codex-bridge`) — правка другой сессии,
не этой; в diff она видна, но не проверяется здесь.

## Что изменено

- Тело: дата сверки; `bun` 1.4 в JS/TS; `agent-browser read`; `rclone`
  вместо `logseq` (Logseq.app удалён, обёртка `~/.local/bin/logseq` падает);
  ловушки pnpm 11+, Node 26 `.ts`, Python 3.15 `strptime`, сломанный `uv tool`
  после смены minor Python, DuckDB 2.0 в сессии агента; строка таблицы
  моментов на новую справку `github-repo-pr.md`; раздел «Нашёл Расхождение»;
  `pnpm` в description.
- Справки: версии и даты; `ast-grep` 0.51 и ловушка custom languages;
  `uv tool audit` переписан (на нынешних окружениях не работает); `uv tool`
  rebuild — `--reinstall` теряет `--with`; Vercel 65 переписан; новая
  `github-repo-pr.md`; `|` внутри кода в ячейках таблиц заменён (ломал таблицу).

## Evidence

Проверено командами в этой сессии:

| Утверждение | Проверка |
|---|---|
| версии инструментов | `TOOL --version` по всему перечню |
| `token-counter` сломан, Python 3.14 удалён | `uv tool list` → `environment not found`; receipt `python = /opt/homebrew/bin/python3.14` |
| `logseq` не работает | `/Applications/Logseq.app` отсутствует |
| `uv tool audit` падает | `uv tool audit ruff` → exit 2, `does not have a lockfile` |
| `pip-audit --path` проверяет tool env | прогон по `~/.local/share/uv/tools/ruff/...` → `No known vulnerabilities found` |
| `--reinstall` теряет `--with` | одноразовый `UV_TOOL_DIR=/tmp/...`: receipt до — с `idna`, после — без |
| ast-grep custom languages | `ast-grep run --help` → `default: ignore`, значения allow/ignore/trust/revoke |
| pnpm 11 defaults | `gh release view v11.0.0 -R pnpm/pnpm`: `minimumReleaseAge` 1 день, `.npmrc` только auth |
| Node `enum` в `.ts` | `node e.ts` падает, `bun e.ts` печатает 0 |
| Python `strptime` | `ValueError` на `strptime('05','%d')` |
| `agent-browser read`, `gh repo read-file`, `--attach`, `--worktree`, `vercel ci`, `deploy --verify`, `setup skills`, `logs requests`, native | их `--help` |
| ссылки | `curl` → 200 для всех внешних URL |
| DuckDB 2.0 agent mode | только документация 2.0 (установлена 1.5.6); `AI_AGENT` в сессии задан |

Разведка трёх субагентов (release notes, даты) — источник кандидатов; каждое
вошедшее утверждение перепроверено командой выше, кроме DuckDB 2.0.

Автовызов за 36 дней (JSONL Claude, `--changed-within 36d`): скил вызван
в 194 из 893 сессий; в 88 из 138 сессий с `npm install|ci`, `tsc`, `uv tool`,
`ffmpeg`, `vercel`, `gh skill|agent-task`, `agent-browser`. 2026-09-25 было
3 из 2080.

## Не вошло — и почему

- Новинки, которые агент найдёт в `--help`: `gh skill` флаги, `npm
  approve-scripts --all`, Node `node:sqlite`, `--process-timeout`, Python
  lazy imports, `frozendict`, bun `fmt`, pnpm `pnx`.
- `plan` (dev-dashboard) — маршрут у `dev-dashboard/AGENTS.md`.
- `rive`, `rustup`, `cmake` — нет действия агента, которое они меняют.
- agent-browser 0.40–0.41 не установлены; `outcome_unknown` 0.39.1 не виден
  в help — не подтверждено.
- Exit code 0 у `uv tool audit` из разведки — неверно, наблюдён 2.

## Вторая редакция: полная переработка по 1smart-simple

Слова владельца: «можно подумать глубже про этот скилл. И как его можно было
бы сделать короче» (вызов `/1smart-simple`). Черновик —
`short-draft.md` рядом: один файл без references, 7,65 тыс. знаков против
24,96 тыс. у тела со справками (×3,3).

Первая волна тройки разбирала первую редакцию; принятое из неё вошло
во вторую: DuckDB 2.0 помечен «по документации», `strptime` и ловушка Node
`.ts` сняты (ошибки громкие; `bun file.ts` остался в перечне), `token-counter`
помечен сломанным, `command -v` → `TOOL --version`, история дат свёрнута
в одну, «Нашёл Расхождение» адресует субагента к родителю и не запрещает
правку по поручению владельца, `approve-builds PKG` вместо интерактива/`--all`,
`run .ts with node` в description. Новый факт той волны: DuckDB 1.5.6
печатает таблицей 40 строк (`(40 shown)`), `-csv` — все (проверено).
Отклонено: путь `experiments/codex-bridge` в строке Codex — правка соседней
сессии по снятию `1codex`, она просила её сохранить.

### Карта потерь

| Было | Решение | Чем покрыто |
|---|---|---|
| 14 справок `references/` | сняты | строка в перечне, ловушка или таблица «Новое» + `--help`/ссылка |
| версии в перечне, история дат | сняты | `TOOL --version`; история — здесь |
| «Вернись В Задачу», формат `TOOL VERSION · … → changed action` | снят | «живой `--help` побеждает этот текст» во вводе |
| имена pin-ов `mavo-short2`, `subfrost-app` | обобщены | «проектный pin сильнее глобального» |
| список bundled skills agent-browser | снят | `agent-browser skills list` |
| npm: `--allow-scripts=PKG` для global/npx, pin записи | снят | `npm help approve-scripts` (проверено: говорит об этом) |
| md-tools: `index_warmup_required` | снят | владелец маршрута `1md-search` (там есть warmup); внешний endpoint оставлен в строке `md` |
| runtime-update: `brew upgrade --dry-run`, «receipt без active path не доказывает» | снят | повтор обеих `--version` и упавшей команды |
| TS 7 `--ignoreConfig`, `--showConfig` | снят | `tsc --help --all` |
| Vercel: таблица «старый путь → route», non-interactive при агенте | сжата в строку; non-interactive снят (ошибка громкая) | `vercel help <cmd>` |
| версии фото-библиотек, scikit-image rc | сняты | `python3 -P -c 'import …'` |
| `gtimeout`, Stats | сняты | `timeout` есть; Stats — не CLI |
| сохранено решение владельца о совместном обновлении (2026-08-19) | одной фразой | — |
