#!/usr/bin/env python3
"""
Universal Agent Launcher — triggers Jules for any agent (1-7).
Agent 7 runs locally (supervisor), agents 1-6 trigger Jules API.
Uses atomic git commits and shared dispatcher lock.
"""
import json
import re
import sys
import os
import subprocess
import urllib.request
import urllib.error
import urllib.parse
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
MAX_RETRIES = 5
MAX_CYCLES_PER_AGENT = 30
STALE_TIMEOUT_MIN = 45
PR_POLL_INTERVAL = 15
PR_POLL_MAX_MINUTES = 15
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

agent_id = ""


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
        print(f"[{agent_id}] git pull failed: {result.stderr}")
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
        print(f"[{agent_id}] git add failed: {add_result.stderr}")
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
        print(f"[{agent_id}] git commit failed: {commit_result.stderr}")
        return False

    push_result = subprocess.run(
        ["git", "push", "origin", "main"],
        capture_output=True, text=True, timeout=30
    )
    if push_result.returncode != 0:
        print(f"[{agent_id}] git push failed: {push_result.stderr}")
    return push_result.returncode == 0


def verify_pushed():
    result = subprocess.run(
        ["git", "log", "origin/main..HEAD", "--oneline"],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode != 0:
        print(f"[{agent_id}] verify_pushed: git log failed, cannot verify")
        return False
    return len(result.stdout.strip()) == 0


def atomic_update(new_data, message):
    for attempt in range(MAX_RETRIES):
        if not git_pull():
            if not git_reset_to_remote():
                print(f"[{agent_id}] Cannot sync with remote, aborting")
                return False

        try:
            with open(LOCK_FILE, encoding="utf-8") as f:
                current = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, PermissionError, UnicodeDecodeError) as e:
            print(f"[{agent_id}] Failed to read {LOCK_FILE}: {e}")
            return False

        for agent_key, state in new_data.get("agents", {}).items():
            if agent_key in current.get("agents", {}):
                for k, v in state.items():
                    if k in current["agents"][agent_key] and isinstance(current["agents"][agent_key][k], dict) and isinstance(v, dict):
                        current["agents"][agent_key][k] = {**current["agents"][agent_key][k], **v}
                    else:
                        current["agents"][agent_key][k] = v
            else:
                current.setdefault("agents", {})[agent_key] = state

        if "last_reset" in new_data:
            current["last_reset"] = new_data["last_reset"]

        atomic_write_json(LOCK_FILE, current)

        if git_commit_and_push(message):
            if verify_pushed():
                return True
            print(f"[{agent_id}] Commit OK but push verify failed, retrying...")
        else:
            print(f"[{agent_id}] Push failed ({attempt + 1}/{MAX_RETRIES})")
        time.sleep(2)

    print(f"[{agent_id}] ERROR: Failed after {MAX_RETRIES} retries")
    return False


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def sanitize_branch_name(name):
    name = re.sub(r'[^\w.\-/]', '-', name)
    name = re.sub(r'-+', '-', name)
    name = name.strip('-')
    return name[:63] if name else "task-branch"


def github_api(endpoint, method="GET", data=None, token=None, _retry_count=0):
    if not token:
        token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print(f"[{agent_id}] No token available")
        return None

    repo = os.environ.get("GITHUB_REPOSITORY", "Koteyka371/ball-royale")
    url = f"https://api.github.com/repos/{repo}/{endpoint}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    body = None
    if data is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(data).encode("utf-8")

    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read().decode("utf-8")
            return json.loads(content) if content.strip() else None
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        if e.code == 403 and "rate limit" in error_body.lower() and _retry_count < 3:
            wait_time = 60 * (_retry_count + 1)
            print(f"[{agent_id}] Rate limited, waiting {wait_time}s (retry {_retry_count + 1}/3)...")
            time.sleep(wait_time)
            return github_api(endpoint, method, data, token, _retry_count + 1)
        if e.code == 404:
            return None
        print(f"[{agent_id}] API {method} {endpoint}: {e.code} {error_body[:200]}")
        return None
    except Exception as e:
        print(f"[{agent_id}] API error: {e}")
        return None


def invoke_jules(task_id, area, prompt, branch_name, token):
    repo_url = f"https://github.com/{os.environ.get('GITHUB_REPOSITORY', 'Koteyka371/ball-royale')}"
    full_prompt = (
        f"Project: Ball Royale — 2D battle royale with AI-controlled balls.\n"
        f"Repository: {repo_url}\n\n"
        f"CONTEXT: You are a coding agent. You have full creative control.\n\n"
        f"TASK: {prompt}\n\n"
        f"BRANCH: Create a new branch called '{branch_name}' for your changes.\n\n"
        f"IMPORTANT RULES:\n"
        f"1. Create branch '{branch_name}' from main\n"
        f"2. Work on the branch '{branch_name}'\n"
        f"3. Create feature branches from '{branch_name}' for each change, merge back\n"
        f"4. Run `git pull origin main` before making changes\n"
        f"5. Commit with clear messages explaining your changes\n"
        f"6. Push branch to origin when done\n"
        f"7. Create a Pull Request with title: [{task_id}] {{descriptive title}}\n"
        f"8. Set PR body to: Task: {task_id}\\n\\n{{description}}\n"
        f"9. DO NOT modify files outside the src/ directory (no workflow changes)\n"
        f"10. Be creative — improve code, refactor, fix bugs you find, add tests\n"
        f"11. Label the PR with 'automated' label\n\n"
        f"You have FULL FREEDOM to modify any file in src/ directory.\n"
        f"Your work will be reviewed and merged by the supervisor agent.\n"
        f"Be ambitious, be creative, be the best AI programmer you can be!"
    )

    url = "https://jules.googleapis.com/jules"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "repoUrl": repo_url,
        "prompt": full_prompt,
    }

    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            task_name = body.get("taskName", "")
            print(f"[{agent_id}] Jules accepted task (task: {task_name})")
            return True
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"[{agent_id}] Jules API error: {e.code} {error_body[:200]}")
        return False
    except Exception as e:
        print(f"[{agent_id}] Jules API exception: {e}")
        return False


def check_pr_created(branch_name, token):
    repo = os.environ.get("GITHUB_REPOSITORY", "Koteyka371/ball-royale")
    owner = repo.split("/")[0]
    encoded_branch = urllib.parse.quote(branch_name, safe="")

    for attempt in range(3):
        url = f"https://api.github.com/repos/{repo}/pulls?head={owner}:{encoded_branch}&state=open"
        req = urllib.request.Request(url, headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        })
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data:
                    print(f"[{agent_id}] PR created: #{data[0].get('number')}")
                    return True
                return False
        except urllib.error.HTTPError as e:
            if e.code == 403 and attempt < 2:
                print(f"[{agent_id}] Rate limited, waiting 30s...")
                time.sleep(30)
            else:
                return False
        except Exception:
            return False
    return False


def find_task_for_agent(agent_id_val, agent_area, lock_data, tasks_data):
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
        if task.get("claimed_by"):
            continue
        mapped_area = AREA_TO_AGENT.get(task_area)
        if mapped_area is None:
            continue
        if task_id not in assigned_remote and mapped_area == agent_area:
            return task_id

    return None


def main():
    global agent_id

    if len(sys.argv) < 2:
        print("Usage: python launch_agent.py <agent-id>")
        print("  agent-id: agent-1, agent-2, ..., agent-6")
        sys.exit(1)

    agent_id = sys.argv[1]

    if not agent_id.startswith("agent-") or not agent_id.split("-")[1].isdigit():
        print(f"Invalid agent ID: {agent_id}")
        sys.exit(1)

    agent_num = int(agent_id.split("-")[1])
    if agent_num < 1 or agent_num > 6:
        print(f"Agent {agent_id} is not a Jules agent (1-6 only)")
        sys.exit(1)

    print("=" * 60)
    print(f"LAUNCHING {agent_id.upper()}")
    print("=" * 60)

    if fcntl is None:
        print(f"[{agent_id}] WARNING: fcntl not available, no file locking")

    lock_fd = None
    try:
        lock_fd = open(DISPATCHER_LOCK, "a+")
        if fcntl:
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except (IOError, OSError):
                print(f"[{agent_id}] Dispatcher is running, waiting...")
                fcntl.flock(lock_fd, fcntl.LOCK_EX)
        else:
            lock_fd.close()
            lock_fd = None

        if not git_pull():
            if not git_reset_to_remote():
                print(f"[{agent_id}] Cannot sync with remote, aborting")
                return 1

        try:
            lock_data = load_json(LOCK_FILE)
            tasks_data = load_json(TASK_FILE)
        except (FileNotFoundError, json.JSONDecodeError, PermissionError, UnicodeDecodeError) as e:
            print(f"[{agent_id}] Failed to load data files: {e}")
            sys.exit(1)

        agent_info = lock_data.get("agents", {}).get(agent_id)
        if not agent_info or not isinstance(agent_info, dict):
            print(f"[{agent_id}] NOT FOUND in {LOCK_FILE}")
            sys.exit(1)

        now = datetime.now(timezone.utc)

        if agent_info.get("status") in ("working", "assigned"):
            started = agent_info.get("started_at")
            if started:
                try:
                    start_dt = datetime.fromisoformat(started)
                    if start_dt.tzinfo is None:
                        start_dt = start_dt.replace(tzinfo=timezone.utc)
                    elapsed_min = (now - start_dt).total_seconds() / 60
                    if elapsed_min > STALE_TIMEOUT_MIN:
                        print(f"[{agent_id}] Stale ({elapsed_min:.0f} min), resetting")
                        update = {"agents": {agent_id: {
                            "status": "idle",
                            "task_id": None,
                            "started_at": None,
                        }}}
                        if not atomic_update(update, f"{agent_id}: reset stale"):
                            print(f"[{agent_id}] Failed to reset stale state")
                            return 1
                        try:
                            lock_data = load_json(LOCK_FILE)
                            agent_info = lock_data.get("agents", {}).get(agent_id, {})
                        except Exception as e:
                            print(f"[{agent_id}] Failed to reload lock data: {e}")
                            return 1
                except (ValueError, TypeError):
                    update = {"agents": {agent_id: {
                        "status": "idle",
                        "task_id": None,
                        "started_at": None,
                    }}}
                    if not atomic_update(update, f"{agent_id}: reset invalid started_at"):
                        print(f"[{agent_id}] Failed to reset invalid started_at")
                        return 1
                    try:
                        lock_data = load_json(LOCK_FILE)
                        agent_info = lock_data.get("agents", {}).get(agent_id, {})
                    except Exception:
                        atomic_update({"agents": {agent_id: {
                            "status": "idle", "task_id": None, "started_at": None,
                        }}}, f"{agent_id}: reset on exception")
                        return 1
            else:
                update = {"agents": {agent_id: {
                    "status": "idle",
                    "task_id": None,
                    "started_at": None,
                }}}
                if not atomic_update(update, f"{agent_id}: reset stale in-progress"):
                    print(f"[{agent_id}] Failed to reset stale in-progress")
                    return 1
                try:
                    lock_data = load_json(LOCK_FILE)
                    agent_info = lock_data.get("agents", {}).get(agent_id, {})
                except Exception:
                    return 1

        cycles_today = agent_info.get("cycles_today", 0)
        if cycles_today >= MAX_CYCLES_PER_AGENT:
            print(f"[{agent_id}] Cycle limit reached ({MAX_CYCLES_PER_AGENT}/{MAX_CYCLES_PER_AGENT})")
            return 0

        if agent_info.get("status") in ("working", "assigned"):
            print(f"[{agent_id}] Agent is busy (status={agent_info.get('status')}), skipping")
            return 0

        area = agent_info.get("area", AGENT_AREAS.get(agent_id, ""))

        task_id = find_task_for_agent(agent_id, area, lock_data, tasks_data)

        if not task_id:
            print(f"[{agent_id}] No tasks found for area {area}")
            print(f"[{agent_id}] Status: idle, nothing to do")
            return 0

        token_env = "JULES_API_KEY_2" if agent_num >= 4 else "JULES_API_KEY"
        token = os.environ.get(token_env, "")
        if not token:
            print(f"[{agent_id}] No {token_env}, skipping")
            return 0

        task = None
        for t in tasks_data.get("tasks", []):
            if t.get("id") == task_id:
                task = t
                break

        if not task:
            print(f"[{agent_id}] Task {task_id} not found in task file")
            return 0

        prompt = task.get("description", "No description provided")
        print(f"[{agent_id}] Task: {task_id}")
        print(f"[{agent_id}] Area: {area}")
        print(f"[{agent_id}] Prompt: {prompt[:100]}...")
        print(f"[{agent_id}] Starting work...")

        now_iso = datetime.now(timezone.utc).isoformat()
        update = {"agents": {agent_id: {
            "status": "working",
            "task_id": task_id,
            "started_at": now_iso,
        }}}
        if not atomic_update(update, f"{agent_id}: start working on {task_id}"):
            print(f"[{agent_id}] Failed to update status")
            return 1

        branch_name = sanitize_branch_name(task_id)
        success = invoke_jules(task_id, area, prompt, branch_name, token)

        if success:
            update = {"agents": {agent_id: {
                "status": "working",
                "cycles_today": cycles_today + 1,
                "task_id": task_id,
            }}}
            if not atomic_update(update, f"{agent_id}: Jules accepted, cycles={cycles_today + 1}"):
                print(f"[{agent_id}] WARNING: Failed to update status after Jules success")
                return 1

            print(f"[{agent_id}] Polling for PR (branch={branch_name})...")
            for i in range(0, PR_POLL_MAX_MINUTES * 60, PR_POLL_INTERVAL):
                if check_pr_created(branch_name, token):
                    print(f"[{agent_id}] PR found!")
                    break
                elapsed = i + PR_POLL_INTERVAL
                print(f"[{agent_id}] Waiting for PR ({elapsed//60}m{elapsed%60}s)...")
                time.sleep(PR_POLL_INTERVAL)
            else:
                print(f"[{agent_id}] PR not found after {PR_POLL_MAX_MINUTES} minutes")
        else:
            update = {"agents": {agent_id: {
                "status": "idle",
                "cycles_today": cycles_today,
                "task_id": None,
                "started_at": None,
            }}}
            if not atomic_update(update, f"{agent_id}: Jules failed, resetting"):
                print(f"[{agent_id}] WARNING: Failed to update status after Jules failure")
                return 1

        print(f"[{agent_id}] Done!")
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
