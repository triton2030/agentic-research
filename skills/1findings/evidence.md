# Evidence `1findings`

## Статус

Рефактор начат 2026-08-31 по новому протоколу `1skill-creation`.

- исходный live-пакет прочитан целиком и сохранён в версии;
- live owner определён через реестр владельцев;
- owner-позиция найдена по корпусу и проверена в исходных файлах;
- новый commander's intent сформирован и подтверждён выбором владельца;
- независимый clean-room смысловой черновик получен без доступа к старому
  пакету;
- Developer Index не нашёл готового эквивалента узкому моменту применения;
- полный candidate собран, а проверка смысловых потерь пакета завершена;
- первая независимая волна завершена двумя terminal-ответами; принятые и
  отклонённые находки записаны в `work/refactor-2026-08-31/review-wave-1.md`;
- вторая, последняя независимая волна завершена; её решения записаны в
  `work/refactor-2026-08-31/review-wave-2.md`;
- прежние exact checks аннулированы новым owner-intent без мысленного протокола;
- exact bytes безусловно утверждены владельцем и установлены в Codex и Claude;
- route-строки восстановлены в двух runtime roots; distribution-потеря закрыта.

## Goal-only exact candidate

- новый body: 736 символов и 27 строк;
- active headings: только `Уникальный Контекст`, `Твоя задача`, `Твоя цель`;
- scan не нашёл мысленного вопроса, последовательности, code block,
  `scripts/`, `add.sh` или команды помощника;
- `qv-skill`: pass;
- `bash -n` bundled scripts: pass;
- `git diff --check`: pass;
- прежние script probes остаются причинно действующими: scripts после них не
  менялись;
- две reviewer-волны относятся к предыдущей procedural версии и не доказывают
  поведение goal-only body;
- behavioral falsifier goal-only эксперимента ещё не прогнан.

## Установка

| Поверхность | Проверка | Результат |
| --- | --- | --- |
| `~/.codex/skills/1findings/` | `qv-skill`; полный directory diff с candidate | pass; точное совпадение |
| `~/.claude/skills/1findings/` | `qv-skill`; `cmp` portable `SKILL.md` и двух scripts | pass; точное portable-совпадение |
| Codex metadata | `agents/openai.yaml`; `allow_implicit_invocation` | установлен |
| Claude platform delta | отсутствие Codex-only `agents/openai.yaml` | соблюдено |
| Internal script edge | оба `add.sh` ссылаются на существующий исполнимый `validate.sh` | pass |
| Global routes | exact route найден в `~/.codex/AGENTS.md:60` и `~/.claude/CLAUDE.md:24` | pass |

Residual risk: goal-only body механически и структурно проверен, но live
поведенческий прогон на target models намеренно остаётся экспериментом.

## Материальные свойства и фальсификаторы

| Property | Falsifier | Наблюдаемый результат |
| --- | --- | --- |
| Mid-trajectory trigger не вызывается заранее | Фраза до побочного сигнала активирует скил | Exact description: before-signal → `not yet`; owner-trigger с допустимым продолжением → `use now` |
| Blocker не откладывается | Реалистичный случай отправляет влияющую на корректность проблему в findings | Exact description: `blocks the current release` не проходит `continue honestly`; обе trajectory-волны оставили blocker в основной работе |
| Запись атомарна | Валидная строка не создаёт ровно один Markdown-файл либо не возвращает адрес | `/tmp/1findings-final.mJNGd6`: один файл и точный адрес после разделения scripts |
| Невалидный формат отвергается | Одночастная строка создаёт находку | Probe вернул ненулевой статус и точную ошибку формата |
| После записи возвращается основная работа | Реалистичная траектория заканчивается отчётом о находке | Trajectory-review завершил путь следующим прерванным действием |
| Recovery не зависает на постоянной ошибке | Ошибка неколлизионной записи повторяется циклом | Final read-only findings-dir дал точный `Permission denied` и немедленный ненулевой выход |
| Metadata не сужает owner-trigger и не принимает blocker | UI prompt допускает только доказанный факт либо любой текущий blocker | Exact `default_prompt` включает «что-то не нравится» / «возможное последствие» и условие «можно честно продолжить» |

## Exact-byte проверки после второй волны

| Проверка | Результат |
| --- | --- |
| `qv-skill` | `Skill is valid!` |
| `bash -n` для обоих scripts | pass |
| `git diff --check` | pass |
| Валидная / невалидная / permanent-error ветви | pass, `/tmp/1findings-final.mJNGd6` |
| Самостоятельные единицы `SKILL.md` | 17 |
| Самостоятельные единицы `scripts/add.sh` | 15 |
| Самостоятельные единицы `scripts/validate.sh` | 7 |
| Самостоятельные единицы `agents/openai.yaml` | 4 |
