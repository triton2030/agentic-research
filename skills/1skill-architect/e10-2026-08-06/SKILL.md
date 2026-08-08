---
name: 1skill-architect
description: >-
  Вызывай ПЕРЕД проектированием нового или существенной переработкой
  существующего skill/control surface: правильные правила часто не меняют
  поведение, если модель не понимает, какой естественный default они должны
  разорвать. Обязателен, когда skill игнорируется, исполняется как ритуал, не
  переносится на новые случаи, разрастается в checklist либо нужно выбрать
  между skill, agent, hook, instruction и script.
---

# skill-architect

**Не начинай с названия, структуры папки или списка возможностей.** Ход:
провал → необходимость → механизм → примеры → поверхность → `description` →
evidence.

Норма проектирования скилов: SKILL.md скила ≤2000 символов; reference-файлов
сколько угодно, каждый ≤2000; переполнение файла решается выносом в новый
reference, не резкой смысла.

## Маршруты — открывай в момент хода (файлы в `references/`)

- вмешательство должно доказать себе необходимость → `why.md`
- берёшь trace, называешь deficit → `trace.md`
- Proof Gate и причинная цепочка → `necessity.md`
- класс пакета и слой enforcement → `class.md`
- проектируешь механизм → `mechanism.md`, `position.md`, `levers.md`
- примеры и конгруэнтность формы → `demos.md`, `demos-examples.md`
- поверхность, граница, stop → `surface.md`, `stop.md`
- пишешь `description` → `discovery.md`, `canvas.md`
- отдаёшь результат владельцу → `frame.md`, `loop.md`
- доказываешь изменение, режешь старое → `evidence-1.md`, `evidence-2.md`,
  `evidence-by-claim.md`
- собираешь пакет, решаешь что вынести → `core-contract.md`, `portable-done.md`
- Claude runtime, метаданные, источники → `platform-1.md`, `platform-2.md`
- узнать провал по имени → `failures.md`; broad audit → `anti-patterns-1…4.md`
- полный аудит landscape, не для одной правки → `deep-audit-1…3.md`, шаблон
  отчёта `deep-audit-report.md`
- термин двусмыслен или меняется сам словарь → `glossary-1…10.md`
