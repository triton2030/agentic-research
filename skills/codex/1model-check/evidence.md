# Evidence

## Status

`candidate`: структура и distribution manual-only версии проверены статически.
Старый late-trigger smoke ниже остаётся историческим evidence и не доказывает
действующую routing policy. Полное adherence, runtime reload и улучшение
решения требуют отдельного behavioral evidence.

## Support Envelope

- Target: Codex `GPT-5.6`, Claude Opus 5 и Claude Fable 5 из `_ops/GOAL.md`.
- Surfaces: tracked runtime owners `skills/{codex,claude}/1model-check/` и
  installed projections `~/.{codex,claude}/skills/1model-check/`.
- Trigger: только явный ручной вызов; внутри разбираются до пяти ещё не
  разобранных assistant-authored `⚡ UNEXPECTED` текущей задачи.

## Claims And Falsifiers

- Structure: system `quick_validate.py` и `qv-skill` на owner и projection.
- Distribution: побайтовая parity `SKILL.md` owner/projection и smoke из чужого
  project cwd.
- Routing: explicit-call positive; implicit trajectory negative; near-miss с
  marker из цитат, файла, tool output или instruction text.
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

## Manual-only delta · 2026-08-31

- Exact owner evidence:
  `_ops/chat-recall/2026-08-31-155258-codex-01a0576e.md#L16`.
- Claude и Codex descriptions начинаются с `Use only when explicitly invoked`;
  Claude frontmatter содержит `disable-model-invocation: true`.
- Codex UI metadata содержит `allow_implicit_invocation: false`.
- Tracked и installed `SKILL.md` обеих платформ совпадают побайтно; Codex
  `agents/openai.yaml` совпадает с установленной projection.
- Structural `md check` по изменённым Markdown-файлам: 10 targets, 0 issues.
- Системный Codex `quick_validate.py` не принимает Claude-native ключ
  `disable-model-invocation`; этот validator-gap не заменён ложным pass.
- Fresh-runtime explicit/implicit smoke после reload не выполнен.

## Limits

- Structural validation не доказывает late-trigger recall или adherence.
- Один успешный replay доказывает возможность, но не вероятностное улучшение.
- Synthetic trigger, прямо создающий пять mismatch, не заменяет holdout replay
  и живой случай.
- Пока behavior comparator и live case не завершены, skill не называется
  принятым.

## Bounded historical replay · 2026-08-22

- Corpus: пять последних `⚡ UNEXPECTED` из Codex task
  `01a0236d-cbaf-72e1-95dd-0832b58fd23b` — snapshot hash drift, отсутствующий
  frozen source object, смешанный cwd verification, missing orchestration
  reference и stale Graphiti runtime status.
- Q1 adherence: pass — пять случаев разделены; для каждого названы ожидание,
  наблюдение, основание, опровержение, коррекция и её результат.
- Q2 verdict: два компактных предположения покрыли все пять случаев без
  выдуманного единого объяснения: locator/receipt принимался за наблюдаемое
  состояние; relative address — за однозначный без resolving context.
- Q3 probe воспроизвёл оба оставшихся класса: live `1orchestration` указывает на
  отсутствующий локальный `references/wording.md`; `1planning` не отделяет
  last-observed external runtime status от live lifecycle evidence.
- Q4 control изменился: вместо 25 отдельных правил выбраны два owner-seam
  repairs; brittle positive tests `test_freeze_corpus.py`, обнаруженные тем же
  probe, переведены на synthetic Git repo без ослабления production dirty/path
  guard. Focused snapshot/evidence suite: 16/16 pass.
- Boundary: это ручной replay из отдельной задачи по просьбе владельца, не
  self-trigger после пятого marker и не live-case proof.
