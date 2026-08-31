#!/usr/bin/env bash
# Создаёт одну находку, не читая существующие.

set -euo pipefail

usage() {
	echo "использование: $(basename "$0") \"что заметил | где | почему вернуться\"" >&2
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

START_DIR="$(pwd)"
[ "$START_DIR" != "/" ] || {
	echo "запусти помощник из папки проекта, не из /" >&2
	exit 1
}

PROJECT_ROOT="$START_DIR"
DIR="$START_DIR"

while :; do
	if [ -d "$DIR/_ops" ] || [ -e "$DIR/.git" ]; then
		PROJECT_ROOT="$DIR"
		break
	fi
	[ "$DIR" = "/" ] && break
	DIR="$(dirname "$DIR")"
done

FINDINGS_DIR="$PROJECT_ROOT/_ops/findings"
mkdir -p "$FINDINGS_DIR"

DATE="$(date +%Y-%m-%d)"
TIME="$(date +%H:%M)"

while :; do
	CAPTURE_ID="$(date +%H%M%S)-$$-$RANDOM"
	FILE="$FINDINGS_DIR/${DATE}-${CAPTURE_ID}.md"

	if (
		set -o noclobber
		{
			echo "# Находка — $DATE — запись:$CAPTURE_ID"
			echo
			printf -- "- %s — %s\n" "$TIME" "$LINE"
		} >"$FILE"
	) 2>/dev/null; then
		break
	fi
done

echo "добавлено → ${FILE#"$PWD"/}"
