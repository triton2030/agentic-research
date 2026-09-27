---
kind: finding
created: "2026-08-24T16:05:00+05:00"
---

# Finding — 2026-08-24 — orchestrate-git-add-vs-git-rm

- 16:05 — `codex_orchestrate.py`: закрывающий шаг делает `git add -f -- <все
  пути allowlist>`; если воркер легитимно удалил tracked-файл через `git rm`
  (путь есть в allowlist, файла нет ни на диске, ни в индексе), git падает
  `fatal: pathspec ... did not match any files`, интеграция всей волны уходит
  в `integration_status=error`, verify пропускается, коммиты оставшихся
  воркеров не создаются. Наблюдалось на волне
  mavo-short2/_workspace/codex-artifacts/20260824T100238Z-22991478 (10
  воркеров, миграция карты v3): 4 ветки закоммичены, 6 остались с работой в
  деревьях; оркестратор докоммитил и слил руками, работа не потерялась.
  Кандидат-фикс: add по путям, существующим на диске, + `git add -A` внутри
  дерева воркера (allowlist уже проверен отдельно), либо `--ignore-removal`
  обход | результат result.json волны, wave.error | дом починки —
  experiments/codex-bridge/codex_orchestrate.py.
