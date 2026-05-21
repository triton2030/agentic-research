# Edit Gate Requires Read Tool, Not Bash Cat

## Observation

Edit tool в harness требует **Read tool** prior на тот же файл — bash cat /
head / tail для preview **не** trackится state-tracker'ом. Когда модель
делает bulk preview через `for f in *.md; do cat $f; done` и потом
запускает Edit на один из тех файлов — Edit фейлится с «File has not been
read yet».

Pattern: **tool-tracking asymmetry**. Bash subprocess читает content, но
harness file-state видит только Read tool calls. Это разделение «efficient
batch preview» (bash) vs «edit-gate priming» (Read tool) скрыто за
эргономикой — оба ощущаются как «прочитал файл», но имеют разный effect
на Edit gate.

Cost: 1-2 failed Edit attempts → retry с Read tool → continue. Visible
friction, не блокер.

## Counter

- 2026-05-21 [Claude Opus 4.7]: при consolidation finding
  `_ops/findings/2026-05-20-gpt-5-5-anonymou.md`. Делал bash cat всех
  findings + self-learning файлов для inventory, потом Edit на один
  finding — fail. Read + Edit retry работало.
- 2026-05-21 [Claude Opus 4.7]: при runtime identity sync для Codex
  `~/.codex/skills/1self-learning/SKILL.md`. Прочитал содержимое через
  bash `cat` в первом ходе разговора. Edit на 2 разных old_string в
  файле — оба fail на «File has not been read yet». Read + параллельный
  retry работало.

## Possible upgrade

Перед planning batch Edit'ов на N файлов — отделить:

1. **Bulk preview** (что в файлах вообще) — bash `cat` / `head` / nav
   `read --extract` приемлемы.
2. **Pre-Edit priming** — для каждого файла где планируется Edit
   нужен явный Read tool call. Параллельный Read трёх-пяти файлов
   дешевле чем serial retry после fail.

Эвристика: «я собираюсь Edit этот файл? → Read tool first».
Не «я прочитал содержимое? → Edit OK».

Связано с `tool-broken-vs-stale-state.md` (модель списывает на tool
вместо проверки state) — sister failure mode, но другая мишень: stale
state vs untracked state.
