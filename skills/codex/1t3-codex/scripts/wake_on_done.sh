#!/usr/bin/env bash
# Wait until a T3 Code run ends or its agent asks a question, then exit.
# Started as a background Bash task, its exit wakes the Claude Code session;
# waiting costs no tokens. It reads T3 Code's own state database read-only.
# That schema is internal and may change with a nightly build, so a read that
# keeps failing for a minute ends the wait with a message instead of hanging.
set -u

if [ $# -lt 1 ]; then
	echo "usage: wake_on_done.sh <runId or threadId> [max minutes, default 120]" >&2
	exit 2
fi
ID="$1"
MAX_MIN="${2:-120}"
DB="${T3CODE_HOME:-$HOME/.t3}/userdata/statev2.sqlite"
RUNS=orchestration_v2_projection_runs
REQUESTS=orchestration_v2_projection_runtime_requests
GRACE=20 # polls of 3 s: one minute

case "$ID" in
*"'"*) echo "[wake] id must not contain quotes: $ID"; exit 2 ;;
run:*) RUN="$ID"; THREAD="" ;;
*) RUN=""; THREAD="$ID" ;;
esac
[ -r "$DB" ] || { echo "[wake] no T3 Code state database at $DB"; exit 1; }

# One row: run, ordinal, status, the kind of a request the agent opened during
# this run and still waits on, the run that goes on after this one (a T3 Code
# restart continuation, else the thread's latest later run) and the run this
# one continues after a restart. A thread id follows the thread's latest run.
row_sql() {
	local where
	if [ -n "$RUN" ]; then
		where="r.run_id = '$RUN'"
	else
		where="r.thread_id = '$THREAD' order by r.ordinal desc limit 1"
	fi
	echo "select r.run_id, r.ordinal, r.status,
		(select q.kind from $REQUESTS q where q.thread_id = r.thread_id
			and q.status = 'pending' and q.kind != 'auth_refresh'
			and q.created_at >= r.requested_at
			order by q.kind = 'user_input' desc limit 1),
		coalesce((select c.run_id from $RUNS c
			where json_extract(c.payload_json, '$.restartContinuationOfRunId') = r.run_id
			limit 1), (select l.run_id from $RUNS l
			where l.thread_id = r.thread_id and l.ordinal > r.ordinal
			order by l.ordinal desc limit 1)),
		json_extract(r.payload_json, '$.restartContinuationOfRunId')
		from $RUNS r where $where"
}

start=$(date +%s)
empty=0
unreadable=0 # T3 Code closes its database for seconds while it restarts
finishing=0  # `waiting`: the provider finished, T3 Code still saves the checkpoint
cancelled=0  # a restart or a restarting reply cancels the run and goes on in a new one
seen=""
note=""
while :; do
	elapsed=$(($(date +%s) - start))
	if ! row=$(sqlite3 -readonly "$DB" "$(row_sql)" 2>&1); then
		unreadable=$((unreadable + 1))
		if [ "$unreadable" -ge "$GRACE" ]; then
			echo "[wake] $ID: cannot read T3 Code state for a minute: $row. T3 Code may be closed, or an update changed its schema"
			exit 1
		fi
		sleep 3
		continue
	fi
	if [ "$unreadable" -gt 0 ]; then
		note="$note; T3 Code state was unreadable for $((unreadable * 3)) s"
		unreadable=0
	fi
	IFS='|' read -r run ordinal status request next continues <<<"$row"
	if [ -z "$status" ]; then
		empty=$((empty + 1))
		if [ "$empty" -ge 40 ]; then
			echo "[wake] $ID: no such run in T3 Code after two minutes"
			exit 1
		fi
		sleep 3
		continue
	fi
	empty=0
	if [ -n "$seen" ] && [ "$run" != "$seen" ]; then
		why=""
		[ "$continues" = "$seen" ] && why="T3 Code restarted, "
		note="$note; ${why}the thread went on as ordinal $ordinal ($run)"
		finishing=0
		cancelled=0
	fi
	seen="$run"
	case "$request" in
	"") ;;
	user_input)
		echo "[wake] $run: the agent asks a question (t3_pending_request_list) after ${elapsed}s, run $status$note"
		exit 0
		;;
	*)
		echo "[wake] $run: the agent waits for a $request approval in the T3 Code app after ${elapsed}s$note"
		exit 0
		;;
	esac
	case "$status" in
	completed | failed | interrupted | rolled_back)
		echo "[wake] $run: $status after ${elapsed}s$note"
		exit 0
		;;
	waiting)
		finishing=$((finishing + 1))
		if [ "$finishing" -ge "$GRACE" ]; then
			echo "[wake] $run: the agent finished after ${elapsed}s; T3 Code is still saving the checkpoint$note"
			exit 0
		fi
		;;
	cancelled)
		if [ -n "$next" ]; then
			[ -n "$RUN" ] && RUN="$next"
			continue
		fi
		cancelled=$((cancelled + 1))
		if [ "$cancelled" -ge "$GRACE" ]; then
			echo "[wake] $run: cancelled after ${elapsed}s$note"
			exit 0
		fi
		;;
	esac
	if [ "$elapsed" -ge $((MAX_MIN * 60)) ]; then
		echo "[wake] $run: still ${status} after ${MAX_MIN} min; the run goes on, start the watch again$note"
		exit 0
	fi
	sleep 3
done
