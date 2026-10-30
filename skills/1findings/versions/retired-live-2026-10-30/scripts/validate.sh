#!/usr/bin/env bash
# Проверяет одну строку находки без чтения существующих записей.

set -euo pipefail

usage() {
	echo "использование: add.sh \"что заметил | где | почему вернуться\"" >&2
	exit 1
}

[ "$#" -eq 1 ] || usage
LINE="$1"

[ -n "${LINE//[[:space:]]/}" ] || {
	echo "находка не может быть пустой" >&2
	exit 1
}

[[ "$LINE" != *$'\n'* && "$LINE" != *$'\r'* ]] || {
	echo "находка должна занимать одну строку" >&2
	exit 1
}

WITHOUT_PIPES="${LINE//|/}"
PIPE_COUNT=$(( ${#LINE} - ${#WITHOUT_PIPES} ))
[ "$PIPE_COUNT" -eq 2 ] || {
	echo "находка должна иметь вид: что заметил | где | почему вернуться" >&2
	exit 1
}

IFS='|' read -r SIGNAL WHERE WHY <<< "$LINE"
for PART in "$SIGNAL" "$WHERE" "$WHY"; do
	[ -n "${PART//[[:space:]]/}" ] || {
		echo "все три части находки должны быть заполнены" >&2
		exit 1
	}
done
