"""Analyze project state and suggest improvements."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_manifest(path: Path) -> dict[str, Any]:
    """Load task manifest."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def analyze_task_completion(manifest: dict[str, Any]) -> dict[str, Any]:
    """Analyze task completion statistics."""
    tasks = manifest.get("tasks", [])
    
    total = len(tasks)
    done = sum(1 for t in tasks if t.get("status") == "done")
    todo = sum(1 for t in tasks if t.get("status") == "todo")
    in_progress = sum(1 for t in tasks if t.get("status") == "in_progress")
    blocked = sum(1 for t in tasks if t.get("status") == "blocked")
    
    areas = {}
    for task in tasks:
        area = task.get("area", "unknown")
        if area not in areas:
            areas[area] = {"total": 0, "done": 0, "todo": 0}
        areas[area]["total"] += 1
        if task.get("status") == "done":
            areas[area]["done"] += 1
        elif task.get("status") == "todo":
            areas[area]["todo"] += 1
    
    risks = {}
    for task in tasks:
        risk = task.get("risk", "unknown")
        if risk not in risks:
            risks[risk] = {"total": 0, "done": 0, "todo": 0}
        risks[risk]["total"] += 1
        if task.get("status") == "done":
            risks[risk]["done"] += 1
        elif task.get("status") == "todo":
            risks[risk]["todo"] += 1
    
    return {
        "total_tasks": total,
        "completed": done,
        "remaining": todo,
        "in_progress": in_progress,
        "blocked": blocked,
        "completion_rate": f"{(done/total*100):.1f}%" if total > 0 else "0%",
        "by_area": areas,
        "by_risk": risks
    }


def analyze_code_coverage(src_dir: Path) -> dict[str, Any]:
    """Analyze source code files."""
    if not src_dir.exists():
        return {"files": 0, "lines": 0, "status": "no source code yet"}
    
    files = list(src_dir.glob("**/*.gd"))
    total_lines = 0
    for f in files:
        with open(f, "r", encoding="utf-8") as fh:
            total_lines += len(fh.readlines())
    
    return {
        "files": len(files),
        "lines": total_lines,
        "avg_lines_per_file": total_lines // len(files) if files else 0
    }


def analyze_tests(test_dir: Path) -> dict[str, Any]:
    """Analyze test files."""
    if not test_dir.exists():
        return {"files": 0, "status": "no tests yet"}
    
    files = list(test_dir.glob("**/test_*.py"))
    return {
        "files": len(files),
        "status": "tests exist" if files else "no tests found"
    }


def suggest_improvements(
    completion: dict[str, Any],
    code: dict[str, Any],
    tests: dict[str, Any]
) -> list[str]:
    """Suggest improvements based on analysis."""
    suggestions = []
    
    if completion["completed"] == 0:
        suggestions.append("No tasks completed yet. Start with low-risk tasks first.")
    elif completion["remaining"] == 0:
        suggestions.append("All tasks completed! Generate new tasks from game_design.md.")
    
    if completion["blocked"] > 0:
        suggestions.append(f"Have {completion['blocked']} blocked tasks. Resolve blockers first.")
    
    if code["files"] == 0:
        suggestions.append("No source code yet. Start implementing ball physics and AI.")
    
    if tests["files"] == 0:
        suggestions.append("No tests found. Add tests for each new feature.")
    
    for area, stats in completion.get("by_area", {}).items():
        if stats["done"] == stats["total"] and stats["total"] > 0:
            suggestions.append(f"Area '{area}' is fully completed!")
        elif stats["todo"] > 3:
            suggestions.append(f"Area '{area}' has {stats['todo']} remaining tasks. Consider prioritizing.")
    
    for risk, stats in completion.get("by_risk", {}).items():
        if risk == "high" and stats["todo"] > 0:
            suggestions.append(f"Have {stats['todo']} high-risk tasks. These need human review.")
    
    return suggestions


def main():
    """Main entry point."""
    manifest_path = Path("agent_tasks.json")
    src_dir = Path("src")
    test_dir = Path("tests")
    
    if not manifest_path.exists():
        print("Error: agent_tasks.json not found")
        return 1
    
    manifest = load_manifest(manifest_path)
    
    print("=" * 60)
    print("BALL ROYALE - PROJECT ANALYSIS")
    print("=" * 60)
    
    completion = analyze_task_completion(manifest)
    print("\n[TASK STATISTICS]")
    print(f"  Total tasks: {completion['total_tasks']}")
    print(f"  Completed: {completion['completed']}")
    print(f"  Remaining: {completion['remaining']}")
    print(f"  In Progress: {completion['in_progress']}")
    print(f"  Blocked: {completion['blocked']}")
    print(f"  Completion Rate: {completion['completion_rate']}")
    
    print("\n[BY AREA]")
    for area, stats in completion.get("by_area", {}).items():
        done = stats["done"]
        total = stats["total"]
        print(f"  {area}: {done}/{total} completed")
    
    print("\n[BY RISK]")
    for risk, stats in completion.get("by_risk", {}).items():
        done = stats["done"]
        todo = stats["todo"]
        print(f"  {risk}: {done} done, {todo} remaining")
    
    code = analyze_code_coverage(src_dir)
    print("\n[CODE]")
    print(f"  Files: {code['files']}")
    print(f"  Lines: {code['lines']}")
    
    tests = analyze_tests(test_dir)
    print("\n[TESTS]")
    print(f"  Files: {tests['files']}")
    print(f"  Status: {tests['status']}")
    
    suggestions = suggest_improvements(completion, code, tests)
    if suggestions:
        print("\n[SUGGESTIONS]")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")
    
    print("\n" + "=" * 60)
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
