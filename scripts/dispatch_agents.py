#!/usr/bin/env python3
"""
Jules Dispatcher — assigns tasks to agents and triggers workflows.
Called by jules-dispatcher.yml after a PR merge or on schedule.
"""
import json
import sys
import os
import urllib.request
import subprocess
from datetime import datetime, timezone

LOCK_FILE = "agent_lock.json"
TASK_FILE = "agent_tasks.json"
MAX_CYCLES = 30


def load_json(path):
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def reset_daily_counters(lock_data):
    """Reset cycle counters if it's a new day."""
    now = datetime.now(timezone.utc)
    last_reset = lock_data.get("last_reset")
    if last_reset is None:
        lock_data["last_reset"] = now.isoformat()
        return lock_data

    last = datetime.fromisoformat(last_reset)
    if last.date() < now.date():
        print("[Dispatcher] New day — resetting cycle counters")
        for agent_id in lock_data["agents"]:
            lock_data["agents"][agent_id]["cycles_today"] = 0
        lock_data["last_reset"] = now.isoformat()

    return lock_data


def find_task_for_agent(agent_id, agent_info, lock_data, tasks_data):
    """Find the best unassigned task for this agent's area."""
    area = agent_info["area"]
    area_tasks = lock_data.get("area_map", {}).get(area, [])
    todo_tasks = [t for t in tasks_data.get("tasks", []) if t.get("status") == "todo"]

    # Get already assigned tasks (by any agent)
    assigned = set()
    for aid, ainfo in lock_data["agents"].items():
        if ainfo.get("task_id") and ainfo.get("status") in ("working", "assigned"):
            assigned.add(ainfo["task_id"])

    # Find first todo task in our area that isn't assigned
    for task_id in area_tasks:
        if task_id not in assigned:
            # Check if task actually exists in agent_tasks.json
            for t in todo_tasks:
                if t["id"] == task_id:
                    return task_id

    # Fallback: find any todo task not in any area and not assigned
    all_area_tasks = set()
    for area_name, task_ids in lock_data.get("area_map", {}).items():
        all_area_tasks.update(task_ids)

    for t in todo_tasks:
        if t["id"] not in all_area_tasks and t["id"] not in assigned:
            return t["id"]

    return None


def trigger_agent_workflow(agent_id):
    """Trigger the agent's GitHub Actions workflow via API."""
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print(f"[Dispatcher] WARNING: No GITHUB_TOKEN, cannot trigger {agent_id}")
        return False

    repo = "Koteyka371/ball-royale"
    workflow = f"jules-agent-{agent_id.split('-')[1]}.yml"
    url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow}/dispatches"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"token {token}",
    }
    payload = {"ref": "main"}

    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"[Dispatcher] Triggered {agent_id} ({workflow})")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"[Dispatcher] ERROR triggering {agent_id}: {e.code} {body}")
        return False
    except Exception as e:
        print(f"[Dispatcher] ERROR triggering {agent_id}: {e}")
        return False


def main():
    print("=" * 60)
    print("JULES DISPATCHER")
    print("=" * 60)

    # Load data
    lock_data = load_json(LOCK_FILE)
    tasks_data = load_json(TASK_FILE)

    # Reset daily counters
    lock_data = reset_daily_counters(lock_data)

    # Find tasks for each idle agent
    assignments = []
    for agent_id, agent_info in lock_data["agents"].items():
        # Skip if already working
        if agent_info.get("status") == "working":
            print(f"[Dispatcher] {agent_id}: already working on {agent_info.get('task_id')}")
            continue

        # Skip if hit daily limit
        if agent_info.get("cycles_today", 0) >= MAX_CYCLES:
            print(f"[Dispatcher] {agent_id}: daily limit reached ({MAX_CYCLES} cycles)")
            continue

        # Find task
        task_id = find_task_for_agent(agent_id, agent_info, lock_data, tasks_data)
        if task_id:
            assignments.append((agent_id, task_id))
            print(f"[Dispatcher] {agent_id}: assigned {task_id}")
        else:
            print(f"[Dispatcher] {agent_id}: no tasks available")

    # Apply assignments
    for agent_id, task_id in assignments:
        lock_data["agents"][agent_id]["task_id"] = task_id
        lock_data["agents"][agent_id]["status"] = "assigned"
        lock_data["agents"][agent_id]["started_at"] = datetime.now(timezone.utc).isoformat()

    # Save lock file
    save_json(LOCK_FILE, lock_data)
    print(f"\n[Dispatcher] Saved {LOCK_FILE} with {len(assignments)} assignments")

    # Trigger workflows
    if assignments:
        print("\n[Dispatcher] Triggering agent workflows...")
        for agent_id, task_id in assignments:
            trigger_agent_workflow(agent_id)
            import time
            time.sleep(2)  # Small delay between triggers
    else:
        print("[Dispatcher] No tasks to assign")

    print("\n[Dispatcher] Done!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
