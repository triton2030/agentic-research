#!/usr/bin/env bash
set -u

if [ "$#" -eq 0 ]; then
	printf 'usage: %s TOOL [TOOL ...]\n' "$0" >&2
	exit 2
fi

repo_root="$PWD"
if command -v git >/dev/null 2>&1; then
	git_root="$(git -C "$PWD" rev-parse --show-toplevel 2>/dev/null || true)"
	if [ -n "$git_root" ]; then
		repo_root="$git_root"
	fi
fi

printf '1cli-tools targeted probe\n'
printf 'cwd: %s\n' "$PWD"
printf 'project root: %s\n' "$repo_root"

exit_code=0
for tool in "$@"; do
	if [[ ! "$tool" =~ ^[[:alnum:]_.+-]+$ ]]; then
		printf 'INVALID handle %s\n' "$tool" >&2
		exit_code=2
		continue
	fi

	local_path="$repo_root/node_modules/.bin/$tool"
	if [ -x "$local_path" ]; then
		printf 'FOUND local %s -> %s\n' "$tool" "$local_path"
	elif command -v "$tool" >/dev/null 2>&1; then
		printf 'FOUND active %s -> %s\n' "$tool" "$(command -v "$tool")"
	else
		printf 'MISS %s\n' "$tool"
	fi
done

exit "$exit_code"
