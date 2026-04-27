# Закрепить active task guard, task closeout и plan sync в meta-скиллах

## Цель
`task-contract`, `project-roadmap` и `instruction-layer` явно поддерживают полный цикл синхронизации задач и плана: обсуждение, работа, проверка критериев, closeout и root-instruction routing.

## Подшаги
- [x] Зафиксировать новый рабочий сигнал в `_ops/INTERVIEW.md`, `_ops/PROJECT-ROADMAP.md` и `_ops/learnings.md`.
- [x] Усилить `task-contract`: активное включение на любое движение вокруг задач, обязательная сверка с текущим task-файлом при работе и повторный вызов после выполнения для отметок, фактического результата и закрытия.
- [x] Усилить `project-roadmap`: сверка плана с историей чата, git evidence и фактически закрытыми task-файлами без превращения PROJECT-ROADMAP в индекс задач.
- [x] Усилить `instruction-layer`: root instruction layer должен прямо требовать частый вызов `task-contract` для обсуждений, правок и task-status movement.
- [x] Обновить корневые инструкции там, где это правило должно быть видно fresh-session агенту.
- [x] Синхронизировать установленные Codex-копии и проверить skill metadata/контракты.

## Критерии приёмки

### Must
- [x] `task-contract` работает как active task-context guard: включается на обсуждение, движение, редактирование или статус вокруг задач и называет связанный task context. — **Evidence**: правка `projects/meta/task-contract--skill-codex/SKILL.md` и metadata.
  **Anchored in**: `_ops/INTERVIEW.md#Рабочий-Режим`
- [x] При реальной правке текста/кода/артефакта `task-contract` проверяет текущую работу против критериев task-файла, а не только создаёт критерии заранее. — **Evidence**: правка `references/task-file-lifecycle.md` с active criteria check.
  **Anchored in**: `_ops/INTERVIEW.md#Рабочий-Режим`
- [x] `task-contract` содержит явный completion closeout loop: после выполнения нетривиальной задачи агент снова вызывает skill и обновляет тот же task-файл. — **Evidence**: правка `projects/meta/task-contract--skill-codex/SKILL.md` и `references/task-file-lifecycle.md`.
  **Anchored in**: `_ops/INTERVIEW.md#Рабочий-Режим`
- [x] `project-roadmap` использует фактическую историю как evidence для синхронизации плана: chat context, git diff/history и закрытые task-файлы, когда они доступны. — **Evidence**: правка `projects/meta/project-roadmap--skill-codex/SKILL.md` и `references/strategy-protocol.md` или `references/file-contracts.md`.
  **Anchored in**: `_ops/INTERVIEW.md#Рабочий-Режим`
- [x] `instruction-layer` требует, чтобы root instructions явно роутировали частый вызов `task-contract` для task-context discussion, edits, status changes и closeout. — **Evidence**: правка `projects/meta/instruction-layer--skill-codex/SKILL.md` / `references/workflow.md` и root docs.
  **Anchored in**: `_ops/INTERVIEW.md#Рабочий-Режим`
- [x] PROJECT-ROADMAP остаётся крупномасштабным планом, а не списком task-файлов. — **Evidence**: в правках есть запрет на task-index drift при чтении закрытых задач.
  **Anchored in**: `_ops/PROJECT-ROADMAP.md#Stage 1`
- [x] Installed Codex skills не расходятся с repo source после правки. — **Evidence**: diff/validation показывает синхронность `/Users/triton/.codex/skills/task-contract`, `/Users/triton/.codex/skills/project-roadmap` и `/Users/triton/.codex/skills/instruction-layer` с `projects/meta/*--skill-codex`.
  **Anchored in**: `_ops/PROJECT-ROADMAP.md#Stage 1`

### Must not
- [x] Project-strategy не редактирует содержимое task-файлов и не переносит acceptance criteria в PROJECT-ROADMAP. — **Why this would be bypassed**: удобно закрывать всё одним владельцем, но это ломает owner-boundary.
- [x] Instruction-layer не дублирует тело task-contract в root docs. — **Why this would be bypassed**: частый вызов можно ошибочно превратить в копию skill contract вместо routing rule.
- [x] Completion closeout не превращается в chat-only receipt без записи в task-файл. — **Why this would be bypassed**: агент может сказать "готово" и забыть обновить рабочий artifact.

### Verification protocol
1. `python3 /Users/triton/.codex/skills/.system/skill-creator/scripts/quick_validate.py projects/meta/task-contract--skill-codex projects/meta/project-roadmap--skill-codex projects/meta/instruction-layer--skill-codex`
   Expected: три skill-папки проходят validation.
   Actual: валидатор single-skill; Codex source, Codex installed и Claude Code source для трёх meta-скиллов проверены по одной, все `Skill is valid!`.
2. `diff -ru --exclude README.md projects/meta/task-contract--skill-codex /Users/triton/.codex/skills/task-contract` и аналогично для `project-roadmap`
   Expected: нет значимого diff после sync.
   Actual: `diff -ru` чистый для `task-contract`, `project-roadmap`, `instruction-layer`; `ensure-ops.sh --check` — no drift.
