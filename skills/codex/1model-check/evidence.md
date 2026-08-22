# Evidence

## Status

`candidate`: структура, distribution и один late-trigger smoke проверены.
Полное adherence и улучшение решения требуют отдельного behavioral evidence.

## Support Envelope

- Target: Codex `GPT-5.6` working set из `_ops/GOAL.md`.
- Harness: Codex desktop; каталог skills доступен модели внутри agentic turn.
- Surface: tracked owner `skills/codex/1model-check/`; installed projection
  `~/.codex/skills/1model-check/`.
- Trigger: каждые пять ещё не разобранных assistant-authored
  `⚡ UNEXPECTED` в текущей задаче.

## Claims And Falsifiers

- Structure: system `quick_validate.py` и `qv-skill` на owner и projection.
- Distribution: побайтовая parity `SKILL.md` owner/projection и smoke из чужого
  project cwd.
- Routing: trajectory-positive после пятого marker; pre-trigger negative после
  четырёх; near-miss с пятью процитированными marker из файла/tool output.
- Behavior: bounded replay до пяти прошлых эпизодов, включая partial/no-common
  case, с anonymized no-skill comparator; затем один live case.

## Executed Evidence · 2026-08-22

- System `quick_validate.py`: pass на tracked owner и installed projection.
- `qv-skill`: pass на tracked owner и installed projection, запущено из
  `/Users/triton/Documents/My_projects/mavo-short2` с абсолютными путями.
- `rumdl`: pass на пяти owner-файлах с отключённым только `MD032`; четыре
  spacing-предупреждения внутри утверждённого output-template сохранены, чтобы
  runtime-текст не отличался от одобренного владельцем.
- Distribution: `cmp` подтвердил побайтовое совпадение двух `SKILL.md`.
- Synthetic read-only late-trigger smoke: ephemeral Codex thread
  `01a02739-a40f-71e0-b35a-8c611862dd05` выполнил пять отдельных `test -e`.
  После пятого assistant-authored marker агент прочитал installed
  `1model-check/SKILL.md` и опубликовал `MODEL-CHECK`.
- Activation verdict: pass в одном synthetic trajectory; вероятностный recall
  и поведение после compaction не доказаны.
- Adherence verdict: fail. Q1 свернул пять случаев в одну строку `S1–S5`
  вместо пяти дословных `ожидал → оказалось`. Q2–Q4, blocker и следующее
  действие присутствовали.
- Harness сообщил, что descriptions сокращены из-за общего skills-context
  budget. Skill всё равно сработал в этом прогоне; устойчивость к truncation
  не доказана.

## Limits

- Structural validation не доказывает late-trigger recall или adherence.
- Один успешный replay доказывает возможность, но не вероятностное улучшение.
- Synthetic trigger, прямо создающий пять mismatch, не заменяет holdout replay
  и живой случай.
- Пока behavior comparator и live case не завершены, skill не называется
  принятым.
