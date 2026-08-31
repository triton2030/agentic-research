#!/usr/bin/env bash
# Создаёт одну находку, не читая существующие.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/validate.sh" "$@"
LINE="$1"

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

	if ERROR="$( (
		set -o noclobber
		{
			echo "# Находка — $DATE — запись:$CAPTURE_ID"
			echo
			printf -- "- %s — %s\n" "$TIME" "$LINE"
		} >"$FILE"
	) 2>&1 )"; then
		break
	fi

	[ -e "$FILE" ] && continue
	printf '%s\n' "$ERROR" >&2
	exit 1
done

echo "добавлено → ${FILE#"$PWD"/}"
