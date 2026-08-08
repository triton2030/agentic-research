---
name: 1skill-architect
description: >
  Вызывай ПЕРЕД созданием/существенной переработкой skill и когда он не
  срабатывает, читается без применения, разрастается или закрывается
  proxy вместо результата. Сначала докажи, что нужен именно skill: неверная
  поверхность создаёт второго owner, а outcome-controller и SOP требуют разных
  форм.
---

# Skill Architect

Проектируй минимальное вмешательство, меняющее решение, не текст. До файлов
скомпилируй decision packet:

1. `JTBD + XY`: trigger, downstream outcome, owner-signal. Владелец может
   определять провал; не изобретай его.
2. `Default → failure → cost → operator`: почему baseline недостаточен.
3. `Admission`: nearest owner и cheapest comparator — rule/check/script/ничего.
   Назови случай вне comparator.
4. `Form`: outcome-controller; SOP лишь когда порядок = correctness.
5. `Evidence`: отдельно activation, uptake/adherence, completion.

Cognitive core пиши causal cells: `operator + почему голую команду обойдут +
правдоподобный anti-example`. «Качественно / учти / не забудь» превращай в
observable stop; критический check ставь в точку решения: reading ≠ application.

Демо: «думай системно» оставляет первый fix. Gate «до verdict назови owner,
future change и cheaper alternative» может сменить seam; «границы учтены» без
иного выбора — anti-example. Тот же gate работает для policy owner.

Фиксированных output-секций нет. `description` — router; `SKILL.md` —
controller; references — условные знания/ветки; scripts — deterministic
operations; mutable truth — у внешнего owner.

- admission, форма, owner, split → [design](references/design.md)
- повторный провал, compression risk → [failures](references/failures.md)
- trigger, transfer, ablation, сдача → [evidence](references/evidence.md)

После packet передай scaffolding/validation/projection runtime-owned skill
creator; owner не обнаружен — stop с gap.

Done: каждый applicable MUST имеет evidence либо `N/A`/`blocked`. Lint и
self-report не доказывают поведение.
