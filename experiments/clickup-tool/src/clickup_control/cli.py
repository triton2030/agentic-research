from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .auth import DEFAULT_TOKEN_FILE, TokenNotFoundError, resolve_token, token_file_mode
from .capabilities import CAPABILITY_MAP
from .client import ClickUpApiError, ClickUpClient, normalize_api_path
from .diagnostics import live_diagnostics, workspace_directory
from .operations import execute_mutation
from .views import configure_view, create_view, delete_view, get_view, get_view_tasks, list_views


def _json_object(value: str | None) -> dict[str, Any]:
    if not value:
        return {}
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise argparse.ArgumentTypeError("Expected a JSON object")
    return parsed


def _json_value(value: str | None) -> Any:
    return None if value is None else json.loads(value)


def _emit(value: object) -> None:
    json.dump(value, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    sys.stdout.write("\n")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="clickup-control")
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="Check credentials and optional live API access")
    doctor.add_argument("--live", action="store_true")
    subparsers.add_parser("capabilities", help="Show routing and capability families")
    subparsers.add_parser("workspaces", help="List authorized Workspaces")

    tree = subparsers.add_parser("tree", help="Build the Space/Folder/List hierarchy")
    tree.add_argument("workspace_id")
    tree.add_argument("--include-archived", action="store_true")

    api = subparsers.add_parser("api", help="Call a documented JSON v2/v3 API endpoint")
    api.add_argument("method", choices=["GET", "HEAD", "OPTIONS", "POST", "PUT", "PATCH", "DELETE"])
    api.add_argument("path")
    api.add_argument("--query", type=_json_object, default={})
    api.add_argument("--body", type=_json_value)

    task = subparsers.add_parser("task", help="Frequent task operations")
    task_subparsers = task.add_subparsers(dest="task_command", required=True)
    task_get = task_subparsers.add_parser("get")
    task_get.add_argument("task_id")
    task_get.add_argument("--workspace-id")
    task_get.add_argument("--custom-id", action="store_true")

    task_search = task_subparsers.add_parser("search")
    task_search.add_argument("workspace_id")
    task_search.add_argument("--page", type=int, default=0)
    task_search.add_argument("--include-closed", action="store_true")
    task_search.add_argument("--subtasks", action=argparse.BooleanOptionalAction, default=True)

    task_create = task_subparsers.add_parser("create")
    task_create.add_argument("list_id")
    task_create.add_argument("--name", required=True)
    task_create.add_argument("--description")
    task_create.add_argument("--assignees", nargs="*", type=int)
    task_create.add_argument("--status")
    task_create.add_argument("--priority", type=int, choices=[1, 2, 3, 4])

    task_update = task_subparsers.add_parser("update")
    task_update.add_argument("task_id")
    task_update.add_argument("--body", type=_json_object, required=True)
    task_update.add_argument("--workspace-id")
    task_update.add_argument("--custom-id", action="store_true")

    task_delete = task_subparsers.add_parser("delete")
    task_delete.add_argument("task_id")
    task_delete.add_argument("--workspace-id")
    task_delete.add_argument("--custom-id", action="store_true")

    view = subparsers.add_parser("view", help="Create, inspect, configure, and delete Views")
    view_subparsers = view.add_subparsers(dest="view_command", required=True)

    view_list = view_subparsers.add_parser("list")
    view_list.add_argument("parent_type", choices=["workspace", "space", "folder", "list"])
    view_list.add_argument("parent_id")

    view_get = view_subparsers.add_parser("get")
    view_get.add_argument("view_id")

    view_create = view_subparsers.add_parser("create")
    view_create.add_argument("parent_type", choices=["workspace", "space", "folder", "list"])
    view_create.add_argument("parent_id")
    view_create.add_argument("--name", required=True)
    view_create.add_argument("--type", required=True, dest="view_type")
    view_create.add_argument("--config", type=_json_object, default={})

    view_configure = view_subparsers.add_parser("configure")
    view_configure.add_argument("view_id")
    view_configure.add_argument("--patch", type=_json_object, required=True)

    view_delete = view_subparsers.add_parser("delete")
    view_delete.add_argument("view_id")

    view_tasks = view_subparsers.add_parser("tasks")
    view_tasks.add_argument("view_id")
    view_tasks.add_argument("--page", type=int, default=0)
    return parser


def _doctor(live: bool) -> dict[str, object]:
    token = resolve_token()
    result: dict[str, object] = {
        "ok": True,
        "token_source": token.source,
        "token_file": str(DEFAULT_TOKEN_FILE),
        "token_file_mode": token_file_mode(),
        "token_exposed": False,
    }
    if live:
        result["live"] = live_diagnostics(ClickUpClient(token.value))
    return result


def _task_command(args: argparse.Namespace, client: ClickUpClient) -> object:
    if args.task_command == "get":
        query = {
            "custom_task_ids": str(args.custom_id).lower(),
            "team_id": args.workspace_id,
            "include_subtasks": "true",
        }
        return client.get(f"/v2/task/{args.task_id}", query).as_dict()
    if args.task_command == "search":
        query = {
            "page": args.page,
            "include_closed": str(args.include_closed).lower(),
            "subtasks": str(args.subtasks).lower(),
        }
        return client.get(f"/v2/team/{args.workspace_id}/task", query).as_dict()
    if args.task_command == "create":
        path = normalize_api_path(f"/v2/list/{args.list_id}/task")
        body = {
            key: value
            for key, value in {
                "name": args.name,
                "description": args.description,
                "assignees": args.assignees,
                "status": args.status,
                "priority": args.priority,
            }.items()
            if value is not None
        }
        return execute_mutation(
            client,
            "POST",
            path,
            body=body,
        )
    if args.task_command == "update":
        path = normalize_api_path(f"/v2/task/{args.task_id}")
        query = {
            "custom_task_ids": str(args.custom_id).lower(),
            "team_id": args.workspace_id,
        }
        return execute_mutation(
            client,
            "PUT",
            path,
            query=query,
            body=args.body,
        )
    if args.task_command == "delete":
        path = normalize_api_path(f"/v2/task/{args.task_id}")
        query = {
            "custom_task_ids": str(args.custom_id).lower(),
            "team_id": args.workspace_id,
        }
        return execute_mutation(
            client,
            "DELETE",
            path,
            query=query,
        )
    raise ValueError(f"Unsupported task command: {args.task_command}")


def _view_command(args: argparse.Namespace, client: ClickUpClient) -> object:
    if args.view_command == "list":
        return list_views(client, args.parent_type, args.parent_id)
    if args.view_command == "get":
        return get_view(client, args.view_id)
    if args.view_command == "create":
        return create_view(
            client,
            args.parent_type,
            args.parent_id,
            args.name,
            args.view_type,
            args.config,
        )
    if args.view_command == "configure":
        return configure_view(client, args.view_id, args.patch)
    if args.view_command == "delete":
        return delete_view(client, args.view_id)
    if args.view_command == "tasks":
        return get_view_tasks(client, args.view_id, args.page)
    raise ValueError(f"Unsupported View command: {args.view_command}")


def run(args: argparse.Namespace) -> object:
    if args.command == "capabilities":
        return CAPABILITY_MAP
    if args.command == "doctor":
        return _doctor(args.live)

    client = ClickUpClient()
    if args.command == "workspaces":
        return workspace_directory(client)
    if args.command == "tree":
        return client.workspace_tree(args.workspace_id, args.include_archived)
    if args.command == "api":
        path = normalize_api_path(args.path)
        return client.request(
            args.method,
            path,
            query=args.query,
            body=args.body,
        ).as_dict()
    if args.command == "task":
        return _task_command(args, client)
    if args.command == "view":
        return _view_command(args, client)
    raise ValueError(f"Unsupported command: {args.command}")


def main() -> None:
    parser = _build_parser()
    try:
        _emit(run(parser.parse_args()))
    except (
        ClickUpApiError,
        TokenNotFoundError,
        ValueError,
        json.JSONDecodeError,
    ) as error:
        _emit({"ok": False, "error": str(error), "type": type(error).__name__})
        raise SystemExit(2) from error
