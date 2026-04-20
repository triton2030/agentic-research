# Learnings

Keep this file under 100 lines.
Rewrite it instead of endlessly appending.
Keep only non-obvious, reusable lessons.
If this file conflicts with the current repo or instruction files, trust the current repo and rewrite this file.

## Active
- Repo is split into three root domains: `knowledge/` (wisdom, guides, examples, research), `projects/{category}/{slug}/` (agents/skills/plugins), `ops/` (operational). See `AGENTS.md` for the canonical layout.
- Before non-trivial work in this repo, read the relevant `knowledge/wisdom-*.md`.
- Before changing project folders or category data, read the matching `knowledge/research/{category}/learnings.md`.
- Keep repeated truths in `knowledge/wisdom-*.md`; `knowledge/guides/` should add reference patterns, templates, or operational detail instead of becoming a second canon.
- External exemplars (other teams' CLAUDE.md, prompts, skills) land in `ops/inbox/` → triaged into `knowledge/examples/{slug}/` with a one-page `takeaways.md`, cited from `knowledge/guides/perfect-*.md` or `knowledge/wisdom-*.md`; otherwise deleted. Inbox does not survive past one ops session.
- Before creating or changing Codex skills, also read `knowledge/practical-guides/codex-skills.md`.
- Default `ops` work maintains `ops/learnings.md`; broader `ops/*` updates, including `NORTH-STAR.md`, happen only on explicit request.
- `ops/learnings.md` is compact project memory, not a task log; keep it current and under 100 lines.
- For rigid review skills, keep one non-bypassable evidence artifact in the core flow; supporting anti-bypass rules should collapse into one compact reference, not sprawl across multiple equally mandatory checks.
- When Codex already has strong narrower skills, prefer a thin router skill over embedding a custom runtime, private orchestration stack, or duplicated evidence workflow inside a new skill.
- If a thin router skill still has no frequent, unique decision point after that simplification, do not keep it installed globally; delete it and let the narrower skills trigger directly.
- For Codex skill frontmatter, any long `description` containing `:` should use a folded scalar (`>`) or safe quoting; otherwise the skill can fail YAML validation even when the workflow itself is sound. Run `quick_validate.py` after edits, not only visual inspection.
- При триаже внешних плагинов/скиллов про агентов и контекст: фильтровать через линзу «авторство, не код». База нужна для скиллов/промптов/файлов, не для написания агентов с нуля. Кодовые детали (KV-cache реализация, sandbox-инфра, выбор Python-библиотек, RDF-онтологии) — пропускать; принципы, изложенные на коде, переформулировать на язык авторства. Правило закреплено в `AGENTS.md` блоком «Назначение».
- Перед установкой стороннего Claude Code скилла в той же категории, где уже есть `my-skills`-скилл, в description обоих явно развести поверхности (например, «breadth across lenses» vs «depth of evidence ledger»), иначе более слабое описание проигрывает приоритету `my-skills` и скилл почти не триггерится.
- Flexible-скилл не обязан навязывать evidence-ledger формат — это поверхность rigid-скиллов (screenshot-design). Не переносить дисциплину одного типа на другой при аудите.
- Когда пользователь просит «скилл для X» — проверить, не iterative audit ли он на самом деле (вызывается часто в ходе итераций, проверяет, не сломали ли что-то правки), а не one-shot generator. Это принципиально меняет форму: rigid review + единый evidence ledger + явные anti-bypass, а не генеративный flow.
- Для audit-скиллов: шаг «define audit target» обязателен до загрузки материала. Папка никогда не сливается в один target по умолчанию — черновики, `-old`, экспорты ломают якоря и делают verdict фиктивным. Правило: «unclear target → ask, never slurp». Плюс binary guard для `.pptx`/`.pdf`/`.key` — скилл не придумывает содержимое непрочитанного файла.
- Когда нужен «скилл со всей мудростью репо» — не складывать всё в один раздутый SKILL.md. Паттерн: тонкий router SKILL.md в `~/.claude/marketplaces/my-skills/skills/<name>/` + `references/` как зеркало канона из `agentic-research/` + `scripts/sync.sh` с `AGENTIC_RESEARCH_DIR` override. Канон остаётся в репо, скилл переживает смену CWD и пользуется приоритетом `my-skills`.
- Когда пользователь просит «напарника по мышлению», а не консультанта-интервьюера: ритм — observe-then-converse, не interrogate-then-converse. Скилл сначала молча сканирует цель (проект или back-scroll разговора), формирует свою картину через линзы systems-thinking + LLM-effectiveness, и только потом открывает диалог. Спросить «что у тебя болит?» до анализа читается как уклонение от позиции и сразу путается с `ops`. Реализация — `system-reflection` в `my-skills`, опирается на `wisdom-systems-thinking.md`, `wisdom-LLM.md`, `wisdom-agents.md`, `perfect-context-engineering.md`, `perfect-project-shape.md`.
