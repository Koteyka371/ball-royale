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
import urllib.error
import time
import tempfile
from datetime import datetime, timezone

try:
    import fcntl
except ImportError:
    fcntl = None

LOCK_FILE = "agent_lock.json"
TASK_FILE = "agent_tasks.json"
DISPATCHER_LOCK = ".dispatcher.lock"
MAX_CYCLES_PER_AGENT = 30
MAX_RETRIES = 5
STALE_TIMEOUT_MIN = 45
SUPERVISOR_ID = "agent-7"

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
    "ai-ball-types": "behaviors",
    "ai-innovation": "innovation",
    "ai-meta": "meta",
    "ai-team": "content",
    "arena-mechanics": "content",
    "arenas": "content",
    "behaviors": "behaviors",
    "bugfix": "meta",
    "content": "content",
    "modes": "content",
    "skills": "content",
    "ui": "content",
    "visuals": "content",
    "innovation": "innovation",
    "meta": "meta",
    "tests": "tests",
}


def atomic_write_json(path, data):
    dir_name = os.path.dirname(os.path.abspath(path))
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile("w", dir=dir_name, suffix=".tmp", delete=False, encoding="utf-8") as tmp:
            json.dump(data, tmp, indent=2, ensure_ascii=False)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_path = tmp.name
        os.replace(tmp_path, path)
    except Exception:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def git_pull():
    result = subprocess.run(
        ["git", "pull", "origin", "main", "--no-edit"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        print(f"[Dispatcher] git pull failed: {result.stderr}")
        if "conflict" in result.stderr.lower() or "merge" in result.stderr.lower():
            subprocess.run(["git", "merge", "--abort"], capture_output=True, timeout=10)
    return result.returncode == 0


def git_fetch():
    result = subprocess.run(
        ["git", "fetch", "origin", "main"],
        capture_output=True, text=True, timeout=30
    )
    return result.returncode == 0


def git_reset_to_remote():
    if not git_fetch():
        return False
    result = subprocess.run(
        ["git", "checkout", "origin/main", "--", LOCK_FILE],
        capture_output=True, text=True, timeout=10
    )
    return result.returncode == 0


def git_commit_and_push(message):
    subprocess.run(["git", "reset", "--mixed", "HEAD", "--", LOCK_FILE], capture_output=True, timeout=10)

    add_result = subprocess.run(
        ["git", "add", LOCK_FILE],
        capture_output=True, text=True, timeout=10
    )
    if add_result.returncode != 0:
        print(f"[Dispatcher] git add failed: {add_result.stderr}")
        return False

    diff_result = subprocess.run(
        ["git", "diff", "--cached", "--quiet", "--", LOCK_FILE],
        capture_output=True, timeout=10
    )
    if diff_result.returncode == 0:
        return True

    commit_result = subprocess.run(
        ["git", "commit", "-m", message],
        capture_output=True, text=True, timeout=10
    )
    if commit_result.returncode != 0:
        print(f"[Dispatcher] git commit failed: {commit_result.stderr}")
        return False

    push_result = subprocess.run(
        ["git", "push", "origin", "main"],
        capture_output=True, text=True, timeout=30
    )
    if push_result.returncode != 0:
        print(f"[Dispatcher] git push failed: {push_result.stderr}")
    return push_result.returncode == 0


def verify_pushed():
    result = subprocess.run(
        ["git", "log", "origin/main..HEAD", "--oneline"],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode != 0:
        print("[Dispatcher] verify_pushed: git log failed, cannot verify")
        return False
    return len(result.stdout.strip()) == 0


def atomic_update(new_data, message):
    for attempt in range(MAX_RETRIES):
        if not git_pull():
            if not git_reset_to_remote():
                print("[Dispatcher] Cannot sync with remote, aborting")
                return False

        try:
            with open(LOCK_FILE, encoding="utf-8") as f:
                current = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, PermissionError, UnicodeDecodeError) as e:
            print(f"[Dispatcher] Failed to read {LOCK_FILE}: {e}")
            return False

        for agent_id_key, state in new_data.get("agents", {}).items():
            if agent_id_key in current.get("agents", {}):
                current["agents"][agent_id_key] = {
                    **current["agents"][agent_id_key],
                    **state,
                }
            else:
                state_with_defaults = {"cycles_today": 0, **state}
                current.setdefault("agents", {})[agent_id_key] = state_with_defaults

        if "last_reset" in new_data:
            current["last_reset"] = new_data["last_reset"]

        atomic_write_json(LOCK_FILE, current)

        if git_commit_and_push(message):
            if verify_pushed():
                return True
            print(f"[Dispatcher] Commit OK but push verify failed, retrying...")
        else:
            print(f"[Dispatcher] Push failed ({attempt + 1}/{MAX_RETRIES})")
        time.sleep(2)

    print(f"[Dispatcher] ERROR: Failed after {MAX_RETRIES} retries")
    return False


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def reset_daily_counters(lock_data):
    now = datetime.now(timezone.utc)
    last_reset = lock_data.get("last_reset")
    if last_reset is None:
        lock_data["last_reset"] = now.isoformat()
        return lock_data, True

    try:
        last = datetime.fromisoformat(last_reset)
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        lock_data["last_reset"] = now.isoformat()
        return lock_data, True

    if last.date() < now.date():
        print("[Dispatcher] New day — resetting cycle counters")
        for agent_id in lock_data.get("agents", {}):
            lock_data["agents"][agent_id].setdefault("cycles_today", 0)
            lock_data["agents"][agent_id]["cycles_today"] = 0
        lock_data["last_reset"] = now.isoformat()
        return lock_data, True

    return lock_data, False


def find_task_for_agent(agent_id, agent_area, lock_data, tasks_data, assigned_in_run):
    todo_tasks = [t for t in tasks_data.get("tasks", []) if t.get("status") == "todo"]

    assigned_remote = set()
    for aid, ainfo in lock_data.get("agents", {}).items():
        if aid == SUPERVISOR_ID:
            continue
        if isinstance(ainfo, dict) and ainfo.get("task_id") and ainfo.get("status") in ("working", "assigned"):
            assigned_remote.add(ainfo["task_id"])

    for task in todo_tasks:
        task_area = task.get("area", "")
        task_id = task.get("id")
        if not task_id:
            continue
        mapped_area = AREA_TO_AGENT.get(task_area)
        if mapped_area is None:
            print(f"[Dispatcher] WARNING: Task {task_id} has unknown area '{task_area}', skipping")
            continue
        if task_id not in assigned_remote and task_id not in assigned_in_run and mapped_area == agent_area:
            return task_id

    return None


def trigger_agent_workflow(agent_id):
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print(f"[Dispatcher] WARNING: No GITHUB_TOKEN, cannot trigger {agent_id}")
        return False

    repo = os.environ.get("GITHUB_REPOSITORY", "Koteyka371/ball-royale")
    try:
        agent_num = agent_id.split("-")[1]
    except (IndexError, AttributeError):
        print(f"[Dispatcher] Invalid agent_id format: {agent_id}")
        return False
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
        print(f"[Dispatcher] ERROR triggering {agent_id}: {e.code} {body[:200]}")
        return False
    except Exception as e:
        print(f"[Dispatcher] ERROR triggering {agent_id}: {e}")
        return False


def main():
    print("=" * 60)
    print("JULES DISPATCHER")
    print("=" * 60)

    if fcntl is None:
        print("[Dispatcher] WARNING: fcntl not available, no file locking")

    lock_fd = None
    try:
        lock_fd = open(DISPATCHER_LOCK, "a+")
        if fcntl:
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except (IOError, OSError):
                print("[Dispatcher] Another dispatcher is running, exiting")
                lock_fd.close()
                lock_fd = None
                return 0
        else:
            lock_fd.close()
            lock_fd = None

        if not git_pull():
            if not git_reset_to_remote():
                print("[Dispatcher] Cannot sync with remote, aborting")
                return 1

        try:
            lock_data = load_json(LOCK_FILE)
        except (FileNotFoundError, json.JSONDecodeError, PermissionError, UnicodeDecodeError) as e:
            print(f"[Dispatcher] Failed to load {LOCK_FILE}: {e}")
            return 1

        try:
            tasks_data = load_json(TASK_FILE)
        except (FileNotFoundError, json.JSONDecodeError, PermissionError, UnicodeDecodeError) as e:
            print(f"[Dispatcher] Failed to load {TASK_FILE}: {e}")
            tasks_data = {"tasks": []}

        if not isinstance(tasks_data, dict) or "tasks" not in tasks_data:
            print(f"[Dispatcher] Malformed {TASK_FILE}, using empty task list")
            tasks_data = {"tasks": []}

        lock_data, day_changed = reset_daily_counters(lock_data)

        now = datetime.now(timezone.utc)
        stale_reset_agents = []
        agents = lock_data.get("agents", {})
        if not isinstance(agents, dict):
            print("[Dispatcher] Invalid agents data in lock file")
            return 1

        for agent_id, agent_info in agents.items():
            if agent_id == SUPERVISOR_ID:
                continue
            if not isinstance(agent_info, dict):
                continue

            status = agent_info.get("status")
            if status not in ("assigned", "working"):
                continue

            started = agent_info.get("started_at")
            if not started:
                stale_reset_agents.append(agent_id)
                lock_data["agents"][agent_id]["status"] = "idle"
                lock_data["agents"][agent_id]["task_id"] = None
                lock_data["agents"][agent_id]["started_at"] = None
                print(f"[Dispatcher] {agent_id}: STALE (no started_at), resetting")
                continue

            try:
                start_dt = datetime.fromisoformat(started)
                if start_dt.tzinfo is None:
                    start_dt = start_dt.replace(tzinfo=timezone.utc)
                elapsed = (now - start_dt).total_seconds() / 60
            except (ValueError, TypeError):
                stale_reset_agents.append(agent_id)
                lock_data["agents"][agent_id]["status"] = "idle"
                lock_data["agents"][agent_id]["task_id"] = None
                lock_data["agents"][agent_id]["started_at"] = None
                print(f"[Dispatcher] {agent_id}: STALE (invalid started_at), resetting")
                continue

            if elapsed > STALE_TIMEOUT_MIN:
                print(f"[Dispatcher] {agent_id}: STALE after {elapsed:.0f} min, resetting")
                lock_data["agents"][agent_id]["status"] = "idle"
                lock_data["agents"][agent_id]["task_id"] = None
                lock_data["agents"][agent_id]["started_at"] = None
                stale_reset_agents.append(agent_id)

        assignments = []
        assigned_in_run = set()
        batch_time = datetime.now(timezone.utc).isoformat()
        for agent_id, agent_info in lock_data.get("agents", {}).items():
            if agent_id == SUPERVISOR_ID:
                continue
            if not isinstance(agent_info, dict):
                continue

            if agent_info.get("status") in ("working", "assigned"):
                print(f"[Dispatcher] {agent_id}: busy ({agent_info.get('status')})")
                continue

            if agent_info.get("cycles_today", 0) >= MAX_CYCLES_PER_AGENT:
                print(f"[Dispatcher] {agent_id}: daily limit reached ({MAX_CYCLES_PER_AGENT} cycles)")
                continue

            agent_area = AGENT_AREAS.get(agent_id, agent_info.get("area", ""))
            task_id = find_task_for_agent(agent_id, agent_area, lock_data, tasks_data, assigned_in_run)
            if task_id:
                assignments.append((agent_id, task_id))
                assigned_in_run.add(task_id)
                print(f"[Dispatcher] {agent_id}: assigned {task_id} (area={agent_area})")
            else:
                print(f"[Dispatcher] {agent_id}: no tasks available in area={agent_area}")

        modified_agents = {}
        agents = lock_data.get("agents", {})
        for aid in stale_reset_agents:
            modified_agents[aid] = {
                "status": "idle",
                "task_id": None,
                "started_at": None,
            }
        for agent_id, task_id in assignments:
            modified_agents[agent_id] = {
                "task_id": task_id,
                "status": "assigned",
                "started_at": batch_time,
            }

        if day_changed:
            for aid in lock_data.get("agents", {}):
                modified_agents[aid] = {"cycles_today": 0}

        update_data = {"agents": modified_agents}
        if day_changed:
            update_data["last_reset"] = lock_data["last_reset"]

        if modified_agents:
            if atomic_update(update_data, f"dispatcher: update {len(modified_agents)} agents"):
                print(f"\n[Dispatcher] Saved {LOCK_FILE}")
            else:
                print("\n[Dispatcher] FAILED to save")
                return 1
        else:
            print("[Dispatcher] Nothing to update")

        if assignments:
            print("\n[Dispatcher] Triggering agent workflows...")
            failed_agents = []
            for agent_id, task_id in assignments:
                if not trigger_agent_workflow(agent_id):
                    failed_agents.append(agent_id)
                time.sleep(2)

            if failed_agents:
                rollback = {"agents": {aid: {
                    "status": "idle",
                    "task_id": None,
                    "started_at": None,
                }} for aid in failed_agents}
                atomic_update(rollback, f"dispatcher: rollback {len(failed_agents)} failed triggers")

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

    finally:
        if lock_fd is not None:
            if fcntl:
                try:
                    fcntl.flock(lock_fd, fcntl.LOCK_UN)
                except Exception:
                    pass
            try:
                lock_fd.close()
            except Exception:
                pass


if __name__ == "__main__":
    sys.exit(main())
