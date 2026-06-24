"""Validate the game project task manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


VALID_STATUSES = {"todo", "in_progress", "done", "blocked"}
VALID_RISKS = {"low", "medium", "high", "critical"}
REQUIRED_TASK_FIELDS = {
    "id",
    "status",
    "area",
    "risk",
    "title",
    "description",
    "allowed_paths",
    "acceptance",
}


class ValidationError(ValueError):
    """Raised when the task manifest violates the expected schema."""


def load_manifest(path: Path) -> dict[str, Any]:
    """Load a JSON task manifest from disk."""
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path}: invalid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ValidationError("manifest root must be an object")
    return data


def validate_manifest(data: dict[str, Any]) -> list[str]:
    """Validate a task manifest and return human-readable warnings."""
    warnings: list[str] = []

    schema_version = data.get("schema_version")
    if schema_version != 1:
        raise ValidationError("schema_version must be 1")

    risk_levels = data.get("risk_levels")
    if set(risk_levels or []) != VALID_RISKS:
        raise ValidationError(f"risk_levels must be exactly {sorted(VALID_RISKS)}")

    merge_policy = data.get("merge_policy")
    if not isinstance(merge_policy, dict):
        raise ValidationError("merge_policy must be an object")

    tasks = data.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ValidationError("tasks must be a non-empty array")

    seen_ids: set[str] = set()
    todo_count = 0
    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            raise ValidationError(f"task #{index + 1} must be an object")
        validate_task(task, index)

        task_id = task["id"]
        if task_id in seen_ids:
            raise ValidationError(f"duplicate task id: {task_id}")
        seen_ids.add(task_id)

        if task["status"] == "todo":
            todo_count += 1

    # Dependency graph validation
    task_map = {t["id"]: t for t in tasks}
    
    # 1. Verify existence of dependencies
    for task in tasks:
        task_id = task["id"]
        dependencies = task.get("depends_on", [])
        if not isinstance(dependencies, list):
            raise ValidationError(f"task {task_id}: depends_on must be an array")
        for dep in dependencies:
            if not isinstance(dep, str):
                raise ValidationError(f"task {task_id}: dependency {dep} must be a string")
            if dep not in task_map:
                raise ValidationError(f"task {task_id}: depends on non-existent task {dep!r}")

    # 2. Cycle detection (DFS)
    visited = {}  # task_id -> state (0=unvisited, 1=visiting, 2=visited)
    
    def dfs(tid):
        visited[tid] = 1  # visiting
        task = task_map[tid]
        for dep in task.get("depends_on", []):
            state = visited.get(dep, 0)
            if state == 1:
                raise ValidationError(f"cyclic dependency detected: {tid} -> {dep}")
            elif state == 0:
                dfs(dep)
        visited[tid] = 2  # visited

    for task in tasks:
        tid = task["id"]
        if visited.get(tid, 0) == 0:
            dfs(tid)

    if todo_count == 0:
        warnings.append("no todo tasks remain")
    elif todo_count < 3:
        warnings.append(f"todo task pool is low: {todo_count} remaining")

    return warnings


def validate_task(task: dict[str, Any], index: int) -> None:
    """Validate one task object from the manifest."""
    missing = REQUIRED_TASK_FIELDS.difference(task)
    if missing:
        raise ValidationError(f"task #{index + 1} missing fields: {sorted(missing)}")

    task_id = task["id"]
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValidationError(f"task #{index + 1} id must be a non-empty string")

    status = task["status"]
    if status not in VALID_STATUSES:
        raise ValidationError(f"task {task_id}: unknown status {status!r}")

    risk = task["risk"]
    if risk not in VALID_RISKS:
        raise ValidationError(f"task {task_id}: unknown risk {risk!r}")

    for field_name in ("area", "title", "description"):
        value = task[field_name]
        if not isinstance(value, str) or not value.strip():
            raise ValidationError(f"task {task_id}: {field_name} must be a non-empty string")

    allowed_paths = task["allowed_paths"]
    if not isinstance(allowed_paths, list) or not allowed_paths:
        raise ValidationError(f"task {task_id}: allowed_paths must be a non-empty array")

    acceptance = task["acceptance"]
    if not isinstance(acceptance, list) or not acceptance:
        raise ValidationError(f"task {task_id}: acceptance must be a non-empty array")


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for task manifest validation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", nargs="?", default="agent_tasks.json")
    args = parser.parse_args(argv)

    try:
        data = load_manifest(Path(args.manifest))
        warnings = validate_manifest(data)
    except ValidationError as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        return 1

    print(f"validation passed: {args.manifest}")
    for warning in warnings:
        print(f"warning: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
