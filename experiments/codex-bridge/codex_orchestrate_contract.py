"""Pure task/status contract helpers for codex_orchestrate."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from codex_defaults import REASONING_EFFORTS

ALLOWED_TASK_KEYS = {
    "id",
    "prompt",
    "files",
    "allow_create",
    "subagents",
    "thread_id",
    "model",
    "effort",
    "contracts_changed",
    "contracts_read",
}
COMPLETED_CODEX_STATUS = "completed"


class UsageError(Exception):
    """CLI/task contract error; report as exit code 2."""


@dataclass(frozen=True)
class TaskSpec:
    id: str
    prompt: str
    files: tuple[str, ...]
    allow_create: bool
    # Разрешение воркеру делить свою задачу на собственных субагентов. Осмысленно
    # только в изолированном дереве: иначе его субагенты пишут в общее.
    subagents: bool = False
    # Тёплый ремонт: продолжить персистентный тред воркера прошлой волны
    # (`results.jsonl` → thread_id) вместо старта с нуля. Контекст задачи у него
    # уже в голове; дерево, файловый контракт и атрибуция — свежие, этой волны.
    thread_id: str | None = None
    # Ярус на задачу, а не на прогон. Без него логически одна волна режется на
    # два флота — пишущие на luna, аудиторы на sol, — и оркестратор дважды
    # платит запуском и мониторингом за одну работу. None = ярус прогона.
    model: str | None = None
    effort: str | None = None
    # Смысловая зона поверх файловой. Непересечение файлов зону не доказывает:
    # два воркера без общих файлов сталкиваются через общий контракт, и merge
    # при этом зелёный. Имя контракта — строка, сверяется буквально, поэтому
    # брать его надо адресом (`path#symbol`), а не описанием.
    contracts_changed: tuple[str, ...] = ()
    contracts_read: tuple[str, ...] = ()

    def to_json(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "prompt": self.prompt,
            "files": list(self.files),
            "allow_create": self.allow_create,
            "subagents": self.subagents,
            "thread_id": self.thread_id,
            "model": self.model,
            "effort": self.effort,
            "contracts_changed": list(self.contracts_changed),
            "contracts_read": list(self.contracts_read),
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


# `id` уходит и в путь worktree, и в имя git-ветки, поэтому проверяется по
# худшему из двух наборов правил. Иначе диверсия не нужна: хватит id вида
# `../x` или `feat/a`, чтобы прогон упал уже после создания части деревьев.
_ID_FORBIDDEN = set(' \t\n/\\~^:?*[]{}@$!"\'`|<>&;()')


def validate_task_id(task_id: str, seen: set[str]) -> None:
    if task_id in seen:
        raise UsageError(f"duplicate task id: {task_id}")
    bad = sorted(_ID_FORBIDDEN & set(task_id))
    if bad:
        raise UsageError(f"{task_id}: id must not contain {' '.join(repr(c) for c in bad)}")
    if task_id.startswith((".", "-")) or task_id.endswith((".", ".lock")) or ".." in task_id:
        raise UsageError(f"{task_id}: id must be usable as a path and a git branch name")
    if len(task_id) > 100 or any(ord(ch) < 32 or ord(ch) == 127 for ch in task_id):
        raise UsageError(f"{task_id!r}: id must be <=100 chars without control characters")


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


def _normalize_contracts(raw: Any, task_id: str, key: str) -> tuple[str, ...]:
    """Список имён контрактов задачи: свободные строки, сверяемые буквально.

    Сверка буквальная, поэтому нормализуется только то, что заведомо не несёт
    смысла: края и повторные пробелы. Имя, набранное двумя воркерами по-разному,
    останется двумя контрактами — это цена свободной строки, и скил велит брать
    имя адресом (`path#symbol`), а не описанием.
    """
    if raw is None:
        return ()
    if not isinstance(raw, list):
        raise UsageError(f"{task_id}: {key} must be a list of strings when provided.")
    seen: list[str] = []
    for item in raw:
        if not isinstance(item, str) or not item.strip():
            raise UsageError(f"{task_id}: {key} must contain non-empty strings.")
        name = " ".join(item.split())
        if name not in seen:
            seen.append(name)
    return tuple(seen)


def check_contract_overlap(tasks: list[TaskSpec]) -> None:
    """Пересечение смысловых зон — отказ до траты, как и пересечение файлов.

    Считается по МЕНЯЮЩЕЙ стороне: владелец контракта один. Чтение чужого
    меняемого контракта — тот самый тихий случай (один менял семантику, второй
    её характеризовал, файлов не делили, merge зелёный), поэтому оно тоже
    отказ: такие две задачи не волна, а очередь.
    """
    changed_by: dict[str, str] = {}
    for task in tasks:
        for name in task.contracts_changed:
            owner = changed_by.get(name)
            if owner is not None:
                raise UsageError(
                    f"{task.id}: contract overlap with {owner}: both change {name!r}"
                )
            changed_by[name] = task.id
    for task in tasks:
        for name in task.contracts_read:
            owner = changed_by.get(name)
            if owner is not None and owner != task.id:
                raise UsageError(
                    f"{task.id}: reads contract {name!r} that {owner} changes "
                    "— sequence these tasks instead of running them in one wave"
                )


def normalize_tasks(project: Path, raw_tasks: Any) -> list[TaskSpec]:
    if not isinstance(raw_tasks, list) or not raw_tasks:
        raise UsageError("Expected a non-empty JSON array of tasks.")

    tasks: list[TaskSpec] = []
    owners: dict[str, str] = {}
    seen_ids: set[str] = set()
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
        validate_task_id(task_id, seen_ids)
        seen_ids.add(task_id)

        prompt = task.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            raise UsageError(f"{task_id}: prompt is required and must be a non-empty string.")

        raw_allow_create = task.get("allow_create", False)
        if type(raw_allow_create) is not bool:
            raise UsageError(f"{task_id}: allow_create must be a boolean when provided.")
        allow_create = raw_allow_create

        raw_subagents = task.get("subagents", False)
        if type(raw_subagents) is not bool:
            raise UsageError(f"{task_id}: subagents must be a boolean when provided.")

        raw_model = task.get("model")
        if raw_model is not None and (not isinstance(raw_model, str) or not raw_model.strip()):
            raise UsageError(f"{task_id}: model must be a non-empty string when provided.")
        model = raw_model.strip() if isinstance(raw_model, str) else None

        raw_effort = task.get("effort")
        if raw_effort is not None and raw_effort not in REASONING_EFFORTS:
            raise UsageError(
                f"{task_id}: effort must be one of {', '.join(REASONING_EFFORTS)} when provided."
            )

        contracts_changed = _normalize_contracts(
            task.get("contracts_changed"), task_id, "contracts_changed"
        )
        contracts_read = _normalize_contracts(
            task.get("contracts_read"), task_id, "contracts_read"
        )

        raw_thread = task.get("thread_id")
        if raw_thread is not None and (not isinstance(raw_thread, str) or not raw_thread.strip()):
            raise UsageError(f"{task_id}: thread_id must be a non-empty string when provided.")
        thread_id = raw_thread.strip() if isinstance(raw_thread, str) else None

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
                subagents=raw_subagents,
                thread_id=thread_id,
                model=model,
                effort=raw_effort,
                contracts_changed=contracts_changed,
                contracts_read=contracts_read,
            )
        )
    check_contract_overlap(tasks)
    return tasks
