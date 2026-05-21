# Multi-Stage Plan Deferred Review

## Observation

Когда задача декомпозируется на несколько последовательных stage
(code → sync → test → docs), модель строит ментальную модель «один план —
один closeout» и откладывает `1work-review` до конца последней stage,
а не делает checkpoint между ними.

Проблема: cumulative file count может уже превысить порог Stop hook
(≥3 файла / sensitive surface) внутри stage B, хотя review после stage A
оставил бы текущий ход под порогом. Wrong direction detected late =
больше rework.

`1work-review` SKILL.md явно содержит правило про multi-stage chain
(«review после каждой stage, не откладывать до конца последней»), но
forward-momentum при чёткой декомпозиции перекрывает это правило —
модель «знает план, дойдёт до конца, потом review».

## Counter

- 2026-05-21 [Claude Opus 4.7]: задача «добавить path-filters в md_graph.py»
  на 4 stage — (A) 6 Edit'ов в md_graph.py с новым helper и фильтрами;
  (B) cp sync копии в `~/.codex/skills/`; (C) smoke-test на изолированной
  структуре; (D) 2 Edit'а в SKILL.md (Claude + Codex) добавляющие
  секцию Scope filters. Cumulative — 4 sensitive-surface файла.
  Review должен был быть после A (≥3 файла уже накопилось). Запустил
  `1work-review` proактивно только после D, всего pipeline'а. Без
  checkpoint между stages — если бы script внутри C показал regression,
  пришлось бы откатывать и A, и B, и C.

## Possible upgrade

- **Skill body of 1work-review** уже содержит multi-stage правило, но
  оно живёт глубже в скиле — модель видит его только когда **вызывает**
  review, а не когда **планирует** chain. Перенести правило в раннее
  место, видимое при планировании (e.g. в `1planning` task contract
  template или session-state hook).
- **Session-state counter** `files_modified_since_last_review` — Stop
  hook твёрже блокирует при ≥3 без `1work-review: да` marker за
  предыдущие 2-3 хода.
- **Memory-side reminder** недостаточен — forward-momentum при чёткой
  декомпозиции перекрывает passive memory recall (тот же mechanism,
  что в `work-review-autofire-skip-on-claude-dir`).
