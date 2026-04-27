#!/usr/bin/env bash
# sync-ops.sh — приводит `_ops/plans/` к списку Stages из `_ops/PROJECT-ROADMAP.md`.
#
# Контракт:
#   - Создаёт отсутствующие `phase-NN-<slug>/` по именам Stages.
#   - Удаляет пустые папки, не совпадающие ни с одним Stage.
#   - Папки с содержимым НЕ удаляет — печатает предупреждение (ручное решение).
#   - task-файлы не трогает: их владелец — `task-contract`.
#   - Идемпотентно: повторный запуск без изменений — no-op.

set -euo pipefail

STRATEGY="_ops/PROJECT-ROADMAP.md"
PLANS="_ops/plans"

if [[ ! -f "$STRATEGY" ]]; then
  echo "sync-ops: $STRATEGY не найден — нет strategy, нет папок" >&2
  exit 1
fi

mkdir -p "$PLANS"

EXPECTED_LIST=$(python3 - "$STRATEGY" <<'PY2'
import sys, re
text = open(sys.argv[1], encoding='utf-8').read()
m = re.search(r'^##\s+Stages\s*$(.*?)(?=^##\s|\Z)', text, re.M | re.S)
if not m:
    sys.exit(0)
body = m.group(1)
for mm in re.finditer(r'^###\s+(\d+)\.\s+(.+?)\s*$', body, re.M):
    num = int(mm.group(1))
    name = mm.group(2).strip()
    slug = name.lower()
    slug = re.sub(r"[^\w\s-]", '', slug, flags=re.U)
    slug = re.sub(r'[\s_]+', '-', slug).strip('-')
    if slug:
        print(f'phase-{num:02d}-{slug}')
PY2
)

if [[ -z "$EXPECTED_LIST" ]]; then
  echo "sync-ops: ни одного Stage не вычитано из $STRATEGY" >&2
  exit 1
fi

count=0
while IFS= read -r e; do
  [[ -z "$e" ]] && continue
  if [[ ! -d "$PLANS/$e" ]]; then
    mkdir -p "$PLANS/$e"
    echo "+ $PLANS/$e"
  fi
  count=$((count + 1))
done <<< "$EXPECTED_LIST"

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
      echo "! $PLANS/$name содержит файлы; Stage удалён из strategy — удали вручную, если траектория поменялась" >&2
    fi
  fi
done

echo "sync-ops: готово, $count папок фаз по strategy."
