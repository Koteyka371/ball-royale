#!/usr/bin/env python3
"""
Jules Dispatcher — assigns tasks to agents and triggers workflows.
Uses the 'area' field from each task in agent_tasks.json for dynamic assignment.
"""
import json
import sys
import os
import urllib.request
import time
from datetime import datetime, timezone

LOCK_FILE = "agent_lock.json"
TASK_FILE = "agent_tasks.json"
MAX_CYCLES = 30

# Agent → area mapping
AGENT_AREAS = {
    "agent-1": "ai-core",
    "agent-2": "behaviors",
    "agent-3": "tests",
    "agent-4": "content",
    "agent-5": "meta",
    "agent-6": "innovation",
}

# Task area → Agent area mapping (task areas from agent_tasks.json)
AREA_TO_AGENT = {
    "ai-core": "ai-core",
    "ai-behaviors": "behaviors",
    "ai-ball-types": "tests",
    "ai-innovation": "innovation",
    "ai-meta": "meta",
    "ai-team": "content",
    "arena-mechanics": "content",
    "arenas": "content",
    "content": "content",
    "modes": "content",
    "skills": "tests",
    "ui": "content",
    "visuals": "content",
}


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


def find_task_for_agent(agent_id, agent_area, lock_data, tasks_data):
    """Find the best unassigned task matching this agent's area."""
    todo_tasks = [t for t in tasks_data.get("tasks", []) if t.get("status") == "todo"]

    # Get already assigned tasks (by any agent)
    assigned = set()
    for aid, ainfo in lock_data["agents"].items():
        if ainfo.get("task_id") and ainfo.get("status") in ("working", "assigned"):
            assigned.add(ainfo["task_id"])

    # Find first todo task in our area that isn't assigned
    for task in todo_tasks:
        task_area = task.get("area", "")
        task_id = task["id"]
        # Map task area to agent area
        mapped_area = AREA_TO_AGENT.get(task_area, task_area)
        if task_id not in assigned and mapped_area == agent_area:
            return task_id

    return None


def trigger_agent_workflow(agent_id):
    """Trigger the agent's GitHub Actions workflow via API."""
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print(f"[Dispatcher] WARNING: No GITHUB_TOKEN, cannot trigger {agent_id}")
        return False

    repo = "Koteyka371/ball-royale"
    agent_num = agent_id.split("-")[1]
    workflow = f"jules-agent-{agent_num}.yml"
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

        # Get agent's area
        agent_area = AGENT_AREAS.get(agent_id, agent_info.get("area", ""))

        # Find task
        task_id = find_task_for_agent(agent_id, agent_area, lock_data, tasks_data)
        if task_id:
            assignments.append((agent_id, task_id))
            print(f"[Dispatcher] {agent_id}: assigned {task_id} (area={agent_area})")
        else:
            print(f"[Dispatcher] {agent_id}: no tasks available in area={agent_area}")

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
            time.sleep(2)  # Small delay between triggers
    else:
        print("[Dispatcher] No tasks to assign")

    # Show remaining tasks per area
    print("\n[Dispatcher] Remaining tasks by area:")
    todo_tasks = [t for t in tasks_data.get("tasks", []) if t.get("status") == "todo"]
    area_counts = {}
    for t in todo_tasks:
        area = t.get("area", "unknown")
        area_counts[area] = area_counts.get(area, 0) + 1
    for area, count in sorted(area_counts.items()):
        print(f"  {area}: {count} tasks")

    print("\n[Dispatcher] Done!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
