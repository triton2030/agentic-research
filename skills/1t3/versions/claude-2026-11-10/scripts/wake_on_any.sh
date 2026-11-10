#!/usr/bin/env bash
# Watch several T3 Code threads or runs at once with wake_on_done.sh.
# In a Claude Code session with an inbox socket every event (a thread ended or
# asks, the tick passed) is posted to the session as a message and the watch
# goes on; the last thread's event ends the script, and that exit wakes the
# session. Without the socket, or when a post fails, the first event ends the
# script, naming the ids still watched: start it again with them.
set -u

usage() {
	echo "usage: wake_on_any.sh [--tick MIN] <runId or threadId>..." >&2
	exit 2
}
TICK=0
if [ "${1:-}" = "--tick" ]; then
	[ $# -ge 2 ] || usage
	TICK="$2"
	shift 2
fi
[ $# -ge 1 ] || usage

DIR="$(cd "$(dirname "$0")" && pwd)"
OUT="$(mktemp -d)"
pids=()
ids=("$@")
cleanup() {
	for pid in "${pids[@]}"; do [ -n "$pid" ] && kill "$pid" 2>/dev/null; done
	rm -rf "$OUT"
}
trap cleanup EXIT

SOCK="${CLAUDE_CODE_MESSAGING_SOCKET:-}"
TOKEN="${CLAUDE_CODE_MESSAGING_TOKEN:-}"
# The session's transcript proves delivery; see post()
LOG="$(compgen -G "$HOME/.claude/projects/*/${CLAUDE_CODE_SESSION_ID:-none}.jsonl" | head -1)"
POST=0
[ -S "$SOCK" ] && [ -n "$TOKEN" ] && [ -n "$LOG" ] && command -v nc >/dev/null &&
	command -v jq >/dev/null && command -v rg >/dev/null && POST=1

# The socket takes JSON lines: the session token, then a user message. The docs
# give only the auth line; the message line is the CLI's own example
# (Claude Code 2.1.321). nc exits 0 even when the session drops the message: a
# plain text line, a changed format, a `hold` or `refuse` setting. So a post
# counts only once its unique mark shows up in the transcript in a peer
# message: a `user` record when it starts a turn, a `queued_command`
# attachment mid-turn. Claude Code writes it when the session takes the
# message: at once when idle, after the running tool call otherwise; a Bash call
# defaults to two minutes, hence three minutes of waiting. Events of other
# threads wait meanwhile, and a missed mark only repeats the event on exit.
# The mark also keeps equal tick messages from being dropped as repeats.
post() {
	local mark tries
	mark="wake-$$-$RANDOM-$(date +%s)"
	{
		jq -cn --arg t "$TOKEN" '{type: "auth", token: $t}'
		jq -cn --arg c "wake_on_any.sh, your T3 watcher: $1
[$mark]" '{type: "user", message: {role: "user", content: $c}}'
		sleep 1
	} | nc -w 5 -U "$SOCK" >/dev/null 2>&1 || return 1
	for ((tries = 0; tries < 180; tries++)); do
		tail -c 2000000 "$LOG" | rg -F "$mark" | jq -R --arg m "$mark" 'fromjson? |
			select((.origin.kind // .attachment.origin.kind) == "peer" and
				(tostring | contains($m)))' | rg -q . && return 0
		sleep 1
	done
	return 1
}

start_watch() {
	bash "$DIR/wake_on_done.sh" "${ids[$1]}" >"$OUT/$1" 2>&1 &
	pids[$1]=$!
}
watched() {
	local j list=()
	for j in "${!pids[@]}"; do [ -n "${pids[$j]}" ] && list+=("${ids[$j]}"); done
	echo "${list[*]}"
}

for i in "${!ids[@]}"; do start_watch "$i"; done

tick_start=$(date +%s)
while :; do
	for i in "${!pids[@]}"; do
		[ -n "${pids[$i]}" ] || continue
		kill -0 "${pids[$i]}" 2>/dev/null && continue
		wait "${pids[$i]}"
		code=$?
		pids[i]=""
		event="$(cat "$OUT/$i")"
		# wake_on_done.sh gives up after its max minutes while the run goes on
		case "$event" in *"start the watch again"*) start_watch "$i" ;; esac
		rest="$(watched)"
		if [ -n "$rest" ] && [ "$POST" = 1 ] &&
			post "${event/start the watch again/wake_on_any watches it again}
[wake] still watched: $rest"; then
			continue
		fi
		echo "$event"
		[ -n "$rest" ] && echo "[wake] still watched: $rest"
		exit "$code"
	done
	if [ "$TICK" -gt 0 ] && [ $(($(date +%s) - tick_start)) -ge $((TICK * 60)) ]; then
		msg="[wake] tick: ${TICK} min passed; all running: $(watched)"
		if [ "$POST" = 1 ] && post "$msg"; then
			tick_start=$(date +%s)
		else
			echo "$msg"
			exit 0
		fi
	fi
	sleep 3
done
