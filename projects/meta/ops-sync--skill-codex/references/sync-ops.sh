#!/usr/bin/env bash
# sync-ops.sh — приводит `_ops/plans/` к списку Stages из `_ops/PROJECT-PLAN.md`.
#
# Вызывается ops-sync после каждой правки блока `## Stages`:
#   bash projects/meta/ops-sync--skill-codex/references/sync-ops.sh
#
# Контракт:
#   - Создаёт отсутствующие `phase-NN-<slug>/` по именам Stages.
#   - Удаляет пустые папки, не совпадающие ни с одним Stage.
#   - Папки с содержимым НЕ удаляет — печатает предупреждение (ручное решение).
#   - task-файлы не трогает: их владелец — `task-contract`.
#   - Идемпотентно: повторный запуск без изменений — no-op.
#
# Эфемерный слой: удаление всего `_ops/plans/` пользователем — штатная операция.

set -euo pipefail

PLAN="_ops/PROJECT-PLAN.md"
PLANS="_ops/plans"

if [[ ! -f "$PLAN" ]]; then
  echo "sync-ops: $PLAN не найден — нет плана, нет папок" >&2
  exit 1
fi

mkdir -p "$PLANS"

# Парсим Stages из PROJECT-PLAN.md.
# Формат Stage-заголовка: `### N. Name [status]` (status и точка опциональны).
EXPECTED_LIST=$(python3 - "$PLAN" <<'PY'
import sys, re
text = open(sys.argv[1], encoding='utf-8').read()
m = re.search(r'^##\s+Stages\s*$(.*?)(?=^##\s|\Z)', text, re.M | re.S)
if not m:
    sys.exit(0)
body = m.group(1)
for mm in re.finditer(r'^###\s+(\d+)\.?\s+(.+?)\s*$', body, re.M):
    num = int(mm.group(1))
    name = mm.group(2)
    name = re.sub(r'\s*\[[ ~x]\]\s*$', '', name).strip()
    slug = name.lower()
    slug = re.sub(r"[^\w\s-]", '', slug, flags=re.U)
    slug = re.sub(r'[\s_]+', '-', slug).strip('-')
    if not slug:
        continue
    print(f'phase-{num:02d}-{slug}')
PY
)

if [[ -z "$EXPECTED_LIST" ]]; then
  echo "sync-ops: ни одного Stage не вычитано из $PLAN" >&2
  exit 1
fi

# Создаём отсутствующие папки.
count=0
while IFS= read -r e; do
  [[ -z "$e" ]] && continue
  if [[ ! -d "$PLANS/$e" ]]; then
    mkdir -p "$PLANS/$e"
    echo "+ $PLANS/$e"
  fi
  count=$((count + 1))
done <<< "$EXPECTED_LIST"

# Удаляем пустые папки, не совпадающие с планом.
shopt -s nullglob
for d in "$PLANS"/*/; do
  [[ -d "$d" ]] || continue
  name=$(basename "$d")
  keep=0
  while IFS= read -r e; do
    [[ -z "$e" ]] && continue
    if [[ "$name" == "$e" ]]; then
      keep=1
      break
    fi
  done <<< "$EXPECTED_LIST"
  if [[ $keep -eq 0 ]]; then
    if [[ -z "$(ls -A "$d")" ]]; then
      rmdir "$d"
      echo "- $PLANS/$name"
    else
      echo "! $PLANS/$name содержит файлы; Stage удалён из плана — удали вручную, если траектория поменялась" >&2
    fi
  fi
done

echo "sync-ops: готово, $count папок фаз по плану."
