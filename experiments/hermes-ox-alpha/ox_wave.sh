#!/bin/bash
# Волна Ox Alpha: один запуск разводит несколько независимых агентов.
#
# Wrapper 1hermes намеренно не программирует декомпозицию — число агентов и
# нарезка работы принадлежат оркестратору. Этот скрипт и есть носитель:
# каждый агент получает свой brief-файл, свою выходную папку и не пересекается
# с соседями ни по чтению, ни по записи.
#
#   TASKS=<папка с *.txt брифами> [PAR=3] [MODE=read|write] bash ox_wave.sh
#
# MODE=read  — только чтение, брифы возвращают вердикт в JSON.
# MODE=write    — агенты пишут прямо в дерево. Годится, когда участки не
#                 пересекаются по файлам: каждый создаёт свои.
# MODE=worktree — правки в отдельном git worktree на каждого агента. Нужен,
#                 когда агенты правят одни и те же файлы. Сливает оркестратор.
set -u
HERMES="$HOME/.claude/skills/1hermes/scripts/hermes_advisor.py"
TASKS=${TASKS:?нужна папка с брифами}
OUT=${OUT:-$TASKS/../runs}
PAR=${PAR:-3}
MODE=${MODE:-read}
CWD=${CWD:-$PWD}
mkdir -p "$OUT"

case "$MODE" in
  read)     EXTRA=(--toolsets file) ;;
  write)    EXTRA=(--allow-write --toolsets file) ;;
  worktree) EXTRA=(--allow-write --worktree --toolsets file) ;;
  *) echo "MODE должен быть read, write или worktree" >&2; exit 2 ;;
esac

run_one() {
  local brief="$1" id
  id=$(basename "$brief" .txt)
  python3 "$HERMES" --cwd "$CWD" \
    --model stealth/ox-alpha --provider nous --reasoning max \
    --max-turns 2000 --timeout-sec 10800 \
    "${EXTRA[@]}" \
    > "$OUT/$id.json" 2> "$OUT/$id.err" < "$brief"
  local ok
  ok=$(python3 -c "import json,sys;print(json.load(open('$OUT/$id.json')).get('ok'))" 2>/dev/null || echo "нет JSON")
  echo "$id: ok=$ok"
}
export -f run_one
export HERMES OUT CWD
export EXTRA_STR="${EXTRA[*]}"

# xargs не переносит массивы, поэтому пересобираем флаги внутри агента
run_wrapper() { EXTRA=($EXTRA_STR); run_one "$1"; }
export -f run_wrapper

ls "$TASKS"/*.txt | xargs -P "$PAR" -I{} bash -c 'run_wrapper "$@"' _ {}
echo "волна завершена; вывод в $OUT"
