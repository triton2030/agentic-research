# Evidence — 1skill-creation

2026-08-26, создание пакета:

- Числа в references сверены с датированными снапшотами
  `knowledge/practical-guides/how-to-write-skills/`
  (research-instruction-wording-adherence-2026-08, research-skill-instruction-
  authoring-jun-aug-2026) и authoring-canon: Instruction Stacking Collapse
  96%→20–60%, CSE 3–7 ограничений, Harness-IF −3.6…−7.4 п.п., Compliance Gap
  0–4%/97%, Signal or Noise −1.3–4.2% Pass@2 и +72–394% токенов, SkillAlchemy
  +19.9 п.п., SIGIL 28%/65%, ASI-Bench −20–26 п.п., 91.8% дефектных скилов.
- Ограничение имени (lowercase латиница/цифры/дефисы, имя = папка) — первичный
  источник agentskills.io/specification через firecrawl developer index.
- `--check` sync_simple_projections: tracked и installed проекции Claude/Codex
  совпадают с owner-ом для 1skill-creation и четырёх правленных соседей.
- Прогон 2026-08-26: субагент с чистым окном верно пересказал функцию и прошёл
  пробный случай «сделай мне скилл оркестрации» (первый шаг — вопросы
  пользователю, не собственная база). Шесть найденных двусмысленностей закрыты
  переформулировкой (лимит вопросов как тип, а не количество; условность
  опроса при уже сказанном; «сверх идеала»; бюджет per-file; повтор прогона;
  cut.md без слова owner). Счёт субагента: 18–21 активная единица тела при
  мягком бюджете ~20. Осознанно оставлено: canon только в сдаче (семейный
  паттерн), мягкость бюджетов при «предложи разделить» (слова владельца),
  статическая субагент-проверка рядом с causal-test заметкой skills-science.
