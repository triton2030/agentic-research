#!/usr/bin/env bash
# Wait until a T3 Code run ends, then exit. Started as a background Bash task,
# its exit wakes the Claude Code session; waiting costs no tokens.
# It reads T3 Code's own state database read-only. That schema is internal and
# may change with a nightly build, so every unexpected answer ends the wait
# with a message instead of hanging.
set -u

if [ $# -lt 1 ]; then
	echo "usage: wake_on_done.sh <runId or threadId> [max minutes, default 120]" >&2
	exit 2
fi
ID="$1"
MAX_MIN="${2:-120}"
DB="${T3CODE_HOME:-$HOME/.t3}/userdata/statev2.sqlite"

case "$ID" in
*"'"*) echo "[wake] id must not contain quotes: $ID"; exit 2 ;;
run:*) QUERY="select status from orchestration_v2_projection_runs where run_id='$ID'" ;;
*) QUERY="select status from orchestration_v2_projection_runs where thread_id='$ID' order by ordinal desc limit 1" ;;
esac
[ -r "$DB" ] || { echo "[wake] no T3 Code state database at $DB"; exit 1; }

start=$(date +%s)
empty=0
while :; do
	if ! status=$(sqlite3 -readonly "$DB" "$QUERY" 2>&1); then
		echo "[wake] cannot read T3 Code state, the schema may have changed: $status"
		exit 1
	fi
	elapsed=$(($(date +%s) - start))
	case "$status" in
	completed | failed | cancelled | interrupted | rolled_back)
		echo "[wake] $ID: $status after ${elapsed}s"
		exit 0
		;;
	waiting)
		echo "[wake] $ID: the agent waits for an answer (t3_pending_request_list) after ${elapsed}s"
		exit 0
		;;
	"")
		empty=$((empty + 1))
		if [ "$empty" -ge 40 ]; then
			echo "[wake] $ID: no such run in T3 Code after two minutes"
			exit 1
		fi
		;;
	esac
	if [ "$elapsed" -ge $((MAX_MIN * 60)) ]; then
		echo "[wake] $ID: still ${status} after ${MAX_MIN} min; the run goes on, start the watch again"
		exit 0
	fi
	sleep 3
done
