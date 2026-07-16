# Structural Critique Playbook

Снимок после сжатия 18 мая 2026.

Playbook для общей оптики структурной критики. Живые скилы адаптируют его под
свой trigger surface; этот файл держит словарь и пороги, чтобы Brooks/Smith
логика не разъезжалась между скилами.

Не tested wisdom. Promotion возможен только после повторного применения в
реальных задачах.

## Sources

- Ousterhout: deep modules, shallow abstractions, cognitive load.
- Brooks: conceptual integrity, essential vs accidental complexity.
- Feathers: legacy seams, characterization, new-in-legacy risk.

## Discipline

1. Диагностируй, не чини. Execution остаётся у owner-а.
2. Если находка не ясна, молчи. Пустой review валиден.
3. Сначала структура, потом стиль, имена и локальная эстетика.
4. Findings должны улучшать ясность через месяцы, а не выигрывать спор сейчас.
5. Если не можешь назвать central model / trigger surface / plan goal,
   это первая находка. Назови её и остановись.

## Brooks Lens

Для структуры артефакта: код, skills, agents, prompts, instructions,
folders, configs.

Ищи:

- **Central model violation**: локальные правки разъедают главный принцип.
- **Shallow abstraction**: интерфейс не экономит чтение реализации.
- **Red flag**: симптом структурной поломки.

Red flags:

- pass-through method;
- interface equals implementation;
- configuration explosion;
- temporal decomposition вместо responsibility split;
- information leakage;
- shallow utility bucket;
- broken window;
- cargo cult;
- dependency surprise;
- new-in-legacy blindness;
- hallucinated API;
- plausibly incorrect behavior.

Brooks finding должен назвать не только проблему, но и лучший shape: какой
контур сохранит central model, deep modules и conceptual integrity.

## Smith Lens

Для траектории выполнения: L1 roadmap/current path, L2 task-файл, L3 subtasks,
done evidence и verification.

Ищи:

- strategy mismatch;
- method as goal;
- one-way door;
- cheaper probe missing;
- best-practice mismatch;
- missing intermediate;
- phantom prerequisite;
- vague boundary;
- hidden coupling;
- done not evidenced;
- future trajectory risk.

Smith finding должен назвать scoped repair: как переформулировать задачу,
разбить работу, проверить done state или выбрать более дешёвый ход.

## Domain Adaptation

`1skill-architect`:

- central model: trigger surface;
- shallow: description как список capabilities;
- red flags: skill explosion, description/body duplication, hidden dependency,
  cargo-cult skill.

`instruction-layer`:

- central model: language-quality and placement of instruction prose;
- shallow: формулировка выглядит красивой, но future model misreads it;
- red flags: lost-in-middle, accidental contract, literal scope, duplicated
  prose, new rule without owner check.

`1ia-audit`:

- central model: authority, truth-vs-view and independent owner seams;
- shallow: folder groups files without contract;
- red flags: config explosion, pass-through hook, ownerless folder,
  new-in-legacy, ownership leak.

Planning skills:

- `project-roadmap`: missing stage, phantom prerequisite, vague stage done.
- `task-contract`: hidden coupling, vague subtask, deleted anchor.
- `plan-drift-watch`: stale referenced stage, drift coupling.
- `strategy-trace`: artifact not serving goal, phantom prerequisite.

Direct evidence-closeout and `pulse-check`:

- use only the universal stop-rule.

## Subagent Fallback

Use `brooks` when:

- artifact feels structurally wrong but the failure is not yet nameable;
- cross-cutting consistency across several artifacts matters;
- a critical instruction/hook/skill change needs last-line structure review.

Use `smith` when:

- roadmap -> task -> subtasks/evidence do not line up;
- plan has 5+ subtasks with handoffs;
- several independent task surfaces need trajectory checks.

Never use Brooks/Smith:

- for typo or tiny rename work;
- as a mandatory gate inside every skill;
- without a specific question and bounded evidence.

## Skill Map

- `1skill-architect`: Brooks full-domain; `brooks` primary fallback.
- `instruction-layer`: language-quality critique; `brooks` available.
- `1ia-audit`: structural owner/shape critique; `brooks` available.
- `project-roadmap`: Smith full-domain; `smith` primary fallback.
- `task-contract`: Smith-light; `smith` available.
- `plan-drift-watch`: Smith-light; `smith` available.
- `strategy-trace`: Brooks + Smith light; both available.
- direct evidence-closeout: stop-rule only; manual fallback.
- `pulse-check`: stop-rule only.

## Promotion

Promote to tested wisdom only when:

1. At least 3 skills used their Brooks/Smith categories on real tasks.
2. Fallback stays conditional: not more often than once per 5-10 days.
3. Duplicated vocabulary across skills did not cause conflict.

Until then this is a playbook, not root wisdom.
