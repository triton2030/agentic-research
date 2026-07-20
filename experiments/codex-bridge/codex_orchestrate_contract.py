"""Pure task/status contract helpers for codex_orchestrate."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

ALLOWED_TASK_KEYS = {"id", "prompt", "files", "allow_create"}
COMPLETED_CODEX_STATUS = "completed"


class UsageError(Exception):
    """CLI/task contract error; report as exit code 2."""


@dataclass(frozen=True)
class TaskSpec:
    id: str
    prompt: str
    files: tuple[str, ...]
    allow_create: bool

    def to_json(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "prompt": self.prompt,
            "files": list(self.files),
            "allow_create": self.allow_create,
        }


def codex_status_value(status: Any) -> str:
    value = getattr(status, "value", None)
    if isinstance(value, str):
        return value
    return str(status)


def codex_turn_completed(status: Any, error: Any) -> bool:
    """Only an explicit completed status is a successful Codex turn."""
    return not error and codex_status_value(status) == COMPLETED_CODEX_STATUS


def worker_status_from_codex_status(status: Any, error: Any) -> str:
    return "completed" if codex_turn_completed(status, error) else "failed"


def paths_overlap(left: str, right: str) -> bool:
    return left == right or left.startswith(right + "/") or right.startswith(left + "/")


def path_allowed(path: str, allowlist: set[str]) -> bool:
    return path in allowlist


def dirty_overlaps(dirty_files: tuple[str, ...] | list[str] | set[str], allowlist: set[str]) -> list[str]:
    return sorted(path for path in dirty_files if any(paths_overlap(path, allowed) for allowed in allowlist))


def _normalize_file(project: Path, raw: Any, allow_create: bool, task_id: str) -> str:
    if not isinstance(raw, str) or not raw.strip():
        raise UsageError(f"{task_id}: files must contain non-empty strings.")
    rel = Path(raw)
    if rel.is_absolute():
        raise UsageError(f"{task_id}: absolute paths are not allowed: {raw}")
    if ".." in rel.parts:
        raise UsageError(f"{task_id}: path traversal is not allowed: {raw}")
    full = (project / rel).resolve()
    try:
        normalized = full.relative_to(project).as_posix()
    except ValueError as exc:
        raise UsageError(f"{task_id}: path escapes project: {raw}") from exc
    if full.exists() and full.is_dir():
        raise UsageError(f"{task_id}: files entry points to a directory: {normalized}")
    if not allow_create and not full.exists():
        raise UsageError(f"{task_id}: file does not exist (use allow_create=true): {normalized}")
    return normalized


def normalize_tasks(project: Path, raw_tasks: Any) -> list[TaskSpec]:
    if not isinstance(raw_tasks, list) or not raw_tasks:
        raise UsageError("Expected a non-empty JSON array of tasks.")

    tasks: list[TaskSpec] = []
    owners: dict[str, str] = {}
    for index, task in enumerate(raw_tasks, start=1):
        if not isinstance(task, dict):
            raise UsageError(f"Task #{index} must be an object.")
        unknown = sorted(set(task) - ALLOWED_TASK_KEYS)
        if unknown:
            raise UsageError(f"Task #{index} has unsupported keys: {', '.join(unknown)}")

        raw_id = task.get("id", None)
        if raw_id is None:
            task_id = f"task-{index}"
        elif isinstance(raw_id, str) and raw_id.strip():
            task_id = raw_id.strip()
        else:
            raise UsageError(f"Task #{index}: id must be a non-empty string when provided.")

        prompt = task.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            raise UsageError(f"{task_id}: prompt is required and must be a non-empty string.")

        raw_allow_create = task.get("allow_create", False)
        if type(raw_allow_create) is not bool:
            raise UsageError(f"{task_id}: allow_create must be a boolean when provided.")
        allow_create = raw_allow_create

        files = task.get("files")
        if not isinstance(files, list) or not files:
            raise UsageError(f"{task_id}: files is required and must be a non-empty list.")

        normalized_files: list[str] = []
        for raw_file in files:
            path = _normalize_file(project, raw_file, allow_create, task_id)
            for existing in normalized_files:
                if paths_overlap(path, existing):
                    raise UsageError(f"{task_id}: duplicate/overlapping files in task: {path} / {existing}")
            for existing, owner in owners.items():
                if paths_overlap(path, existing):
                    raise UsageError(f"{task_id}: file overlap with {owner}: {path} / {existing}")
            normalized_files.append(path)
            owners[path] = task_id

        tasks.append(
            TaskSpec(
                id=task_id,
                prompt=prompt.strip(),
                files=tuple(normalized_files),
                allow_create=allow_create,
            )
        )
    return tasks
