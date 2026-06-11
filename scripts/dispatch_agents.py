#!/usr/bin/env python3
"""
Jules Dispatcher — assigns tasks to agents and triggers workflows.
Uses atomic git commits to prevent race conditions on agent_lock.json.
"""
import json
import sys
import os
import subprocess
import urllib.request
import time
from datetime import datetime, timezone

LOCK_FILE = "agent_lock.json"
TASK_FILE = "agent_tasks.json"
MAX_CYCLES = 30
MAX_RETRIES = 5

AGENT_AREAS = {
    "agent-1": "ai-core",
    "agent-2": "behaviors",
    "agent-3": "tests",
    "agent-4": "content",
    "agent-5": "meta",
    "agent-6": "innovation",
}

AREA_TO_AGENT = {
    "ai-core": "ai-core",
    "ai-behaviors": "behaviors",
    "ai-ball-types": "tests",
    "ai-innovation": "innovation",
    "ai-meta": "meta",
    "ai-team": "content",
    "arena-mechanics": "content",
    "arenas": "content",
    "bugfix": "meta",
    "content": "content",
    "modes": "content",
    "skills": "tests",
    "ui": "content",
    "visuals": "content",
    "innovation": "innovation",
    "meta": "meta",
    "tests": "tests",
}


def git_pull():
    """Pull latest changes from remote."""
    result = subprocess.run(
        ["git", "pull", "origin", "main", "--no-edit"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        print(f"[Dispatcher] git pull failed: {result.stderr}")
    return result.returncode == 0


def git_commit_and_push(message):
    """Atomically commit and push changes. Returns True on success."""
    subprocess.run(["git", "add", LOCK_FILE], capture_output=True, timeout=10)

    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        capture_output=True, timeout=10
    )
    if result.returncode == 0:
        return True  # No changes to commit

    subprocess.run(
        ["git", "commit", "-m", message],
        capture_output=True, text=True, timeout=10
    )

    result = subprocess.run(
        ["git", "push", "origin", "main"],
        capture_output=True, text=True, timeout=30
    )
    return result.returncode == 0


def atomic_update(new_data, message):
    """Pull, update lock file, commit, push with retry."""
    for attempt in range(MAX_RETRIES):
        git_pull()

        # Load fresh data after pull
        with open(LOCK_FILE) as f:
            current = json.load(f)

        # Merge: only update agent states, keep everything else
        for agent_id, state in new_data.get("agents", {}).items():
            current["agents"][agent_id] = state
        if "last_reset" in new_data:
            current["last_reset"] = new_data["last_reset"]

        # Write
        with open(LOCK_FILE, "w") as f:
            json.dump(current, f, indent=2, ensure_ascii=False)

        if git_commit_and_push(message):
            return True

        print(f"[Dispatcher] Push failed, retrying ({attempt + 1}/{MAX_RETRIES})...")
        time.sleep(2)

    print(f"[Dispatcher] ERROR: Failed after {MAX_RETRIES} retries")
    return False


def load_json(path):
    with open(path) as f:
        return json.load(f)


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

    assigned = set()
    for aid, ainfo in lock_data["agents"].items():
        if ainfo.get("task_id") and ainfo.get("status") in ("working", "assigned"):
            assigned.add(ainfo["task_id"])

    for task in todo_tasks:
        task_area = task.get("area", "")
        task_id = task["id"]
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

    git_pull()

    lock_data = load_json(LOCK_FILE)
    tasks_data = load_json(TASK_FILE)

    lock_data = reset_daily_counters(lock_data)

    # Clean up stale agents (assigned/working for > 45 minutes)
    now = datetime.now(timezone.utc)
    for agent_id, agent_info in lock_data["agents"].items():
        status = agent_info.get("status")
        started = agent_info.get("started_at")
        if status in ("assigned", "working") and started:
            elapsed = (now - datetime.fromisoformat(started)).total_seconds() / 60
            if elapsed > 45:
                print(f"[Dispatcher] {agent_id}: STALE after {elapsed:.0f} min, resetting")
                lock_data["agents"][agent_id]["status"] = "idle"
                lock_data["agents"][agent_id]["task_id"] = None
                lock_data["agents"][agent_id]["started_at"] = None

    assignments = []
    for agent_id, agent_info in lock_data["agents"].items():
        if agent_info.get("status") == "working":
            print(f"[Dispatcher] {agent_id}: already working on {agent_info.get('task_id')}")
            continue

        if agent_info.get("status") == "assigned":
            print(f"[Dispatcher] {agent_id}: already assigned {agent_info.get('task_id')}")
            continue

        if agent_info.get("cycles_today", 0) >= MAX_CYCLES:
            print(f"[Dispatcher] {agent_id}: daily limit reached ({MAX_CYCLES} cycles)")
            continue

        agent_area = AGENT_AREAS.get(agent_id, agent_info.get("area", ""))
        task_id = find_task_for_agent(agent_id, agent_area, lock_data, tasks_data)
        if task_id:
            assignments.append((agent_id, task_id))
            print(f"[Dispatcher] {agent_id}: assigned {task_id} (area={agent_area})")
        else:
            print(f"[Dispatcher] {agent_id}: no tasks available in area={agent_area}")

    if assignments:
        update_data = {"agents": {}}
        for agent_id, task_id in assignments:
            update_data["agents"][agent_id] = {
                **lock_data["agents"][agent_id],
                "task_id": task_id,
                "status": "assigned",
                "started_at": datetime.now(timezone.utc).isoformat(),
            }

        if atomic_update(update_data, f"dispatcher: assign {len(assignments)} tasks"):
            print(f"\n[Dispatcher] Saved {LOCK_FILE} with {len(assignments)} assignments")
        else:
            print("\n[Dispatcher] FAILED to save assignments")
            return 1
    else:
        print("[Dispatcher] No tasks to assign")

    if assignments:
        print("\n[Dispatcher] Triggering agent workflows...")
        for agent_id, task_id in assignments:
            trigger_agent_workflow(agent_id)
            time.sleep(2)

    print("\n[Dispatcher] Remaining tasks by area:")
    todo_tasks = [t for t in tasks_data.get("tasks", []) if t.get("status") == "todo"]
    area_counts = {}
    for t in todo_tasks:
        area = t.get("area", "unknown")
        area_counts[area] = area_counts.get(area, 0) + 1
    for area, count in sorted(area_counts.items()):
        print(f"  {area}: {count}")

    print("\n[Dispatcher] Done!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
