#!/bin/bash
# Prints one line with the live versions of the tools whose traps in SKILL.md
# depend on a version. SKILL.md runs it through !`...` when the skill loads.
# Always exits 0: a failing !`...` command aborts the whole skill load.

tools=(node npm pnpm tsc duckdb rg gh vercel ast-grep depcruise python3)
# Without timeout one hanging tool would hold the skill load indefinitely.
command -v timeout >/dev/null 2>&1 || { echo "версии не сняты: нет timeout"; exit 0; }
tmp=$(mktemp -d) || { echo "версии не сняты"; exit 0; }

for i in "${!tools[@]}"; do
  (
    t=${tools[$i]}
    if ! command -v "$t" >/dev/null 2>&1; then
      echo "$t нет" > "$tmp/$i"; exit
    fi
    # A number is taken only from a successful --version: error text such as
    # "requires Node.js >=22.18.0" also contains one.
    if out=$(timeout 5 "$t" --version 2>&1) &&
      [[ $out =~ ([0-9]+\.[0-9]+(\.[0-9]+)?) ]]; then
      line="$t ${BASH_REMATCH[1]}"
    else
      line="$t ошибка"
    fi
    if [[ $t == node ]]; then
      line="$line ($(command -v node | sed "s|^$HOME|~|"))"
    fi
    echo "$line" > "$tmp/$i"
  ) &
done
wait

line=""
for i in "${!tools[@]}"; do
  part=$(cat "$tmp/$i" 2>/dev/null)
  line="${line:+$line · }${part:-${tools[$i]} ошибка}"
done
rm -rf "$tmp"
echo "$line"
exit 0
