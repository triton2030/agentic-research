# Findings — 2026-05-22 — gpt-5-5 — sess:anonymou

- 00:39 — 1md-navigator проверка | knowledge/ md_health: description coverage 10/37, no broken links | file-level ориентация полезна, но corpus descriptions пока ограничивают качество меню чтения
- 00:40 — _ops routing conflict | root/GOAL/1findings use _ops/findings, but _ops/AGENTS.md still routes hot-findings to problems/ | owner-route рассинхрон обнаружен во время проверки navigator usefulness
- 01:14 — md-navigator: wrong corpus root remains a UX risk | experiments/md-embedding-server/scripts/navigator/index_status.py find_corpus_root_for exists but status/search do not suggest parent/child index roots | user may index a subfolder then query repo root and get misleading NO INDEX/warmup
- 01:16 — md-embedding-server audit | субагенты и CLI подтверждают распад модели: backend вырос из navigator/embedding server в Markdown workbench; нужен staged shrink, не слепой full rewrite
