#!/usr/bin/env python3
"""
Agent Status Dashboard — shows what all 6 agents are doing.
Usage: python status_agents.py
"""
import json
import sys
from datetime import datetime, timezone

LOCK_FILE = "agent_lock.json"
TASK_FILE = "agent_tasks.json"
MAX_CYCLES_PER_AGENT = 30
NUM_AGENTS = 7


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    try:
        lock_data = load_json(LOCK_FILE)
    except (FileNotFoundError, json.JSONDecodeError, PermissionError, UnicodeDecodeError) as e:
        print(f"Failed to load {LOCK_FILE}: {e}")
        return 1

    try:
        tasks_data = load_json(TASK_FILE)
    except (FileNotFoundError, json.JSONDecodeError, PermissionError, UnicodeDecodeError) as e:
        print(f"Failed to load {TASK_FILE}: {e}")
        tasks_data = {"tasks": []}

    if not isinstance(tasks_data, dict) or "tasks" not in tasks_data:
        tasks_data = {"tasks": []}

    now = datetime.now(timezone.utc)

    print("=" * 70)
    print("JULES AGENT DASHBOARD")
    print(f"Time: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 70)

    tasks = tasks_data.get("tasks", [])
    done = [t for t in tasks if t.get("status") == "done"]
    todo = [t for t in tasks if t.get("status") == "todo"]
    print(f"\nTasks: {len(done)} done / {len(todo)} todo / {len(tasks)} total")
    if tasks:
        print(f"Progress: {len(done)/len(tasks)*100:.1f}%")

    print(f"\n{'Agent':<20s} {'Status':<12s} {'Area':<14s} {'Task':<30s} {'Cycles':<8s}")
    print("-" * 84)

    total_cycles = 0
    active_agents = 0

    for agent_id in sorted(lock_data["agents"].keys()):
        info = lock_data["agents"][agent_id]
        status = info.get("status", "idle")
        area = info.get("area", "?")
        task_id = info.get("task_id") or "-"
        cycles = info.get("cycles_today", 0)
        total_cycles += cycles

        if status == "working":
            active_agents += 1
            status_display = "\033[92mworking\033[0m"
        elif status == "assigned":
            status_display = "\033[93massigned\033[0m"
        else:
            status_display = "\033[90midle\033[0m"

        task_display = task_id[:28] if len(task_id) > 28 else task_id

        print(f"{agent_id:<20s} {status_display:<21s} {area:<14s} {task_display:<30s} {cycles}/{MAX_CYCLES_PER_AGENT}")

    print("-" * 84)
    print(f"\nActive agents: {active_agents}/{NUM_AGENTS - 1}")
    print(f"Total cycles today: {total_cycles}/{MAX_CYCLES_PER_AGENT * (NUM_AGENTS - 1)}")

    if total_cycles > MAX_CYCLES_PER_AGENT * (NUM_AGENTS - 1) * 0.83:
        print(f"\n\033[91mWARNING: Rate limit approaching! {total_cycles}/{MAX_CYCLES_PER_AGENT * (NUM_AGENTS - 1)} cycles used\033[0m")

    print(f"\n{'='*70}")
    print("COMPLETED TASKS")
    print(f"{'='*70}")
    for t in done:
        print(f"  [done] {t['id']}")

    print()


if __name__ == "__main__":
    main()
