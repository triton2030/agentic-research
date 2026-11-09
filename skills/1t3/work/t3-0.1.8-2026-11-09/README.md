# Сверка с T3 Code 0.1.8-nightly, 2026-11-09

**Граница.** Адресная правка Claude-версии: `references/common.md` и
`references/claude-code.md`, после проверяющего — ещё `gemini-media.md`.
`SKILL.md`, `inside-t3.md` и скрипты не менялись. Codex-версия `skills/codex/1t3-codex/` не тронута: она
отстала с 2026-10-28 и требует отдельной переработки. Снимок —
`../../versions/claude-2026-11-09/`; прежнее состояние — `claude-2026-11-05`
плюс раздел из `2026-11-05-before-worktree-cleanup` и git.

**Заказ.** «проверь скил т3, там много обновлений наверное нам сам скил тоже
стоит обновить»; набросок одобрен словами «Да, вноси».

**Источники.** Установлен T3 Code `0.1.8-nightly.20261108.4367`. Коммиты
`pingdotgg/t3code` с 2026-10-01 по 2026-11-09, документы `docs/user/` и
`docs/orchestration-v2/orchestrator-mcp-server.md`, живые описания
инструментов сервера `t3`, `~/.t3/userdata/settings.json`.

## Что изменено

| Место | Было | Стало и основание |
| --- | --- | --- |
| `common.md`, усилие Codex | `high`, никогда `max` (2026-11-05) | из таблицы `1orchestration`: установленная копия уже так говорила с 2026-11-06, репо отстал; в таблице Sol и Terra — `max`, как в глобальном `CLAUDE.md` владельца |
| `claude-code.md`, пример запуска | усилие `high` зашито | `<effort>`: значение живёт в одном месте, у `1orchestration` |
| `claude-code.md`, `runtimeMode` | «на уровне одобрения тред ждёт» | ниже `full-access` ждёт, и `auto` тоже: новый режим T3, ревью провайдера спрашивает о нестандартном (`docs/user/permission-modes.md`) |
| `claude-code.md`, settled | «по документации три дня», очистка может удалить копию | порог — `sidebarAutoSettleAfterDays` (у владельца 1, по умолчанию 7 с коммита d4247a5a); удаление копии — только при включённой очистке Settings → Worktrees → Cleanup, по умолчанию выключена (`docs/user/project-settings.md`) |
| `claude-code.md`, продолжение | новый раунд в длинном треде — новым тредом | ещё вариант: `t3_thread_send` с `freshContext: true` — по описанию инструмента, не проверено |
| `claude-code.md`, сбои | `capability_denied` | плюс `runtime_mode_escalation_denied`: вход ниже Full access, новый вход по умолчанию Auto (коммит 917ce994, `docs/user/outside-agents.md`) |

## Что проверено и оставлено

- `wake_on_done.sh` и `wake_on_any.sh` на текущей базе: на завершённом ходе
  и треде выходят сразу, на идущем ждут.
- `t3 thread start/send/show` и их флаги прежние; `~/.t3/bin` не в PATH.
- Имена и параметры инструментов, на которые ссылается скил, не изменились.
- Побудки внешнего вызывающего не появилось: `next` в ответе
  `t3_thread_wait` ставится, только когда конец будит тред-родителя; в коде
  T3 нет каналов Claude Code. Сторож остаётся путём.

## Что не добавлено

Новые инструменты (`t3_queue`, `t3_thread_search`, `t3_thread_organize`,
`t3_thread_transfer`, `t3_worktree_handoff`, запланированные задачи) и
`untilDelegatedWorkSettled`: описания говорят сами, а правило 2026-10-31 —
скил говорит только то, чего нет в MCP.

## Попутно

`1orchestration` (Claude): правка 2026-11-06 жила только в установленном
пакете; перенесена в tracked owner — `skills/1orchestration/README.md`.

## Проверка

- Проба `new-a` (Sonnet `high`, песочница `probe.py`, без вызовов T3): «отдай Codex Sol тикет в своей копии, продолжим завтра». Порядок по транскрипту: `SKILL.md` → `common.md` → `claude-code.md` → таблица `1orchestration`. Взял `max` и `serviceTier: default` из таблицы, `full-access` с доводом «ниже ждёт согласия»; к завтра учёл settled через `sidebarAutoSettleAfterDays` и поиск `settled: true` или по `threadId`; копию не удаляет; на `runtime_mode_escalation_denied` — перелогин с Full access, права не понижает.
- Проверяющий другой семьи: тред Codex `gpt-6.1-sol/max`, запущен по самому скилу в копии `/tmp/t3review/review-wt` на `e0abc3f5`; `threadId` `mcp:launch:20a66ec2bcf660dc493d7c467c59c351243a58fab506bcad2b8481a530c971b8`, 558 с. В изменённых строках ошибок не нашёл; `git status` копии остался пустым. Две находки в нетронутых местах, обе приняты:
  - «A Gemini thread can't hear or see» (`gemini-media.md`, строка Gemini в `common.md`) — неверно для вложений: `docs/user/providers-antigravity.md` («receives images and audio directly…»). Замер: картинка 8×8 через `t3_attachment_prepare_upload`, POST на `http://127.0.0.1:3773` + `relativeUrl` (HTTP 204) и `attachments` в `t3_thread_launch` дошла до Gemini Flash — ответ «Красный», тред `mcp:launch:392943319fe4641bb8547ce52b18c17f1d8d6e6ab17e1e0d3f0e4cae5e6be93a`. Аудио, PDF и видео — по документации. Скрипт остаётся для путей и флагов.
  - «`runOnWorktreeCreate` did not run» (`claude-code.md`) — по коду T3 `c6ca605` `ThreadLaunchService.ts` выполняет скрипт до старта агента (асинхронный — параллельно). Замер 2026-10-30 был один, а скрипт subfrost копирует только `design-catalog/node_modules`; новый замер не делался — в тексте «по коду T3».
- Снимок после находок — `../../versions/claude-2026-11-09-v2/`. Проба `new-a` эти два места не покрывала: поведение по ним пробой не проверено.
