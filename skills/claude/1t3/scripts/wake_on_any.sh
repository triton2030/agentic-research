#!/usr/bin/env bash
# Watch several T3 Code threads or runs at once with wake_on_done.sh and exit
# when the first of them ends or asks, or when the optional tick passes.
# One background task then wakes the Claude Code session instead of one per
# thread plus a separate timer. Start it again with the ids still running.
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
	for pid in "${pids[@]}"; do kill "$pid" 2>/dev/null; done
	rm -rf "$OUT"
}
trap cleanup EXIT

for i in "${!ids[@]}"; do
	bash "$DIR/wake_on_done.sh" "${ids[$i]}" >"$OUT/$i" 2>&1 &
	pids+=("$!")
done

start=$(date +%s)
while :; do
	for i in "${!pids[@]}"; do
		if ! kill -0 "${pids[$i]}" 2>/dev/null; then
			wait "${pids[$i]}"
			code=$?
			cat "$OUT/$i"
			others=("${ids[@]:0:$i}" "${ids[@]:$((i + 1))}")
			[ ${#others[@]} -gt 0 ] && echo "[wake] still watched: ${others[*]}"
			exit "$code"
		fi
	done
	if [ "$TICK" -gt 0 ] && [ $(($(date +%s) - start)) -ge $((TICK * 60)) ]; then
		echo "[wake] tick: ${TICK} min passed; all running: ${ids[*]}"
		exit 0
	fi
	sleep 3
done
