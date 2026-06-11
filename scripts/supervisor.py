#!/usr/bin/env python3
"""
Agent 7 — Supervisor & Orchestrator.
Monitors agent lock, verifies CI, merges PRs, fixes failed CI via Jules API,
ensures task continuity, triggers dispatcher when needed.
"""
import json
import sys
import os
import subprocess
import urllib.request
import urllib.error
import time
from datetime import datetime, timezone

try:
    import fcntl
except ImportError:
    fcntl = None

LOCK_FILE = "agent_lock.json"
TASK_FILE = "agent_tasks.json"
SUPERVISOR_LOCK = ".supervisor.lock"
MAX_RETRIES = 5
CYCLE_LIMIT = 30
STALE_TIMEOUT_MIN = 45


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def atomic_write_json(path, data):
    import tempfile
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
        print(f"[Supervisor] git pull failed: {result.stderr}")
    return result.returncode == 0


def git_fetch():
    subprocess.run(
        ["git", "fetch", "origin", "main"],
        capture_output=True, text=True, timeout=30
    )


def git_reset_to_remote():
    git_fetch()
    result = subprocess.run(
        ["git", "checkout", "origin/main", "--", LOCK_FILE],
        capture_output=True, text=True, timeout=10
    )
    return result.returncode == 0


def git_commit_and_push(message):
    subprocess.run(["git", "add", LOCK_FILE], capture_output=True, timeout=10)

    diff_result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        capture_output=True, timeout=10
    )
    if diff_result.returncode == 0:
        return True

    commit_result = subprocess.run(
        ["git", "commit", "-m", message],
        capture_output=True, text=True, timeout=10
    )
    if commit_result.returncode != 0:
        print(f"[Supervisor] git commit failed: {commit_result.stderr}")
        return False

    push_result = subprocess.run(
        ["git", "push", "origin", "main"],
        capture_output=True, text=True, timeout=30
    )
    if push_result.returncode != 0:
        print(f"[Supervisor] git push failed: {push_result.stderr}")
    return push_result.returncode == 0


def verify_pushed():
    result = subprocess.run(
        ["git", "log", "origin/main..HEAD", "--oneline"],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode != 0:
        return True
    return len(result.stdout.strip()) == 0


def save_and_push(new_data, message):
    for attempt in range(MAX_RETRIES):
        if not git_pull():
            if not git_reset_to_remote():
                return False

        try:
            with open(LOCK_FILE, encoding="utf-8") as f:
                current = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[Supervisor] Failed to read {LOCK_FILE}: {e}")
            return False

        for key, value in new_data.items():
            if key in current and isinstance(current[key], dict) and isinstance(value, dict):
                for k, v in value.items():
                    if k in current[key] and isinstance(current[key][k], dict) and isinstance(v, dict):
                        current[key][k] = {**current[key][k], **v}
                    else:
                        current[key][k] = v
            else:
                current[key] = value

        atomic_write_json(LOCK_FILE, current)

        if git_commit_and_push(message):
            if verify_pushed():
                return True
            print(f"[Supervisor] Commit OK but push verify failed, retrying...")
        else:
            print(f"[Supervisor] Push failed ({attempt + 1}/{MAX_RETRIES})")
        time.sleep(2)

    print(f"[Supervisor] ERROR: Failed after {MAX_RETRIES} retries")
    return False


def github_api(endpoint, method="GET", data=None, token=None):
    if not token:
        token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("[Supervisor] No token available")
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
            return json.loads(content) if content.strip() else {"message": "empty response"}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"[Supervisor] API {method} {endpoint}: {e.code} {error_body[:300]}")
        return None
    except Exception as e:
        print(f"[Supervisor] API error: {e}")
        return None


def get_ci_status(sha):
    if not sha:
        return "pending"
    token = os.environ.get("GITHUB_TOKEN", "")

    pr_result = github_api(f"commits/{sha}/pull-request", token=token)
    if pr_result:
        mergeable = pr_result.get("mergeable")
        merge_state = pr_result.get("mergeable_state", "")
        if mergeable is False or mergeable == "dirty":
            return "failure"
        if mergeable is True and merge_state == "clean":
            return "success"

    url = f"https://api.github.com/repos/{os.environ.get('GITHUB_REPOSITORY', 'Koteyka371/ball-royale')}/commits/{sha}/check-runs?per_page=30"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    })

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return "pending"

    check_runs = data.get("check_runs", [])
    if not check_runs:
        return "pending"

    blocking_conclusions = {"failure", "timed_out", "cancelled", "action_required", "stale"}
    for run in check_runs:
        conclusion = run.get("conclusion")
        status = run.get("status", "")
        if conclusion in blocking_conclusions:
            return "failure"
        if status != "completed":
            return "pending"

    return "success"


def ensure_ci_waits(sha, max_minutes=60):
    if not sha:
        return True

    print(f"[Supervisor] Waiting for CI on {sha[:8]}...")

    for i in range(0, max_minutes * 2, 15):
        status = get_ci_status(sha)
        print(f"[Supervisor] CI status ({i//60}m{i%60}s): {status}")

        if status == "success":
            print("[Supervisor] CI passed!")
            return True
        elif status == "failure":
            print("[Supervisor] CI failed")
            return False

        time.sleep(15)

    print("[Supervisor] CI wait timeout")
    return False


def invoke_jules(task_id, area, prompt, branch_name, token):
    if not token:
        token = os.environ.get("JULES_API_KEY", "")
    if not token:
        print("[Supervisor] No Jules token available")
        return False

    repo_url = f"https://github.com/Koteyka371/ball-royale"
    full_prompt = (
        f"Project: Ball Royale — 2D battle royale with AI-controlled balls.\n"
        f"Repository: {repo_url}\n\n"
        f"CONTEXT: You are a coding agent. You have full creative control.\n\n"
        f"TASK: {prompt}\n\n"
        f"BRANCH: Use existing branch '{branch_name}' for your changes.\n\n"
        f"IMPORTANT RULES:\n"
        f"1. Work ONLY on the branch '{branch_name}'\n"
        f"2. Create feature branches from '{branch_name}' for each change, merge back\n"
        f"3. Run `git pull origin main` before making changes\n"
        f"4. Commit with clear messages explaining your changes\n"
        f"5. Push branch to origin when done\n"
        f"6. DO NOT create a pull request\n"
        f"7. DO NOT modify files outside the src/ directory (no workflow changes)\n"
        f"8. Be creative — improve code, refactor, fix bugs you find, add tests\n"
        f"9. After pushing, commit a small status update: echo '{task_id} in progress' >> AGENTS.md\n\n"
        f"You have FULL FREEDOM to modify any file in src/ directory.\n"
        f"Your work will be reviewed by the supervisor agent.\n"
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
            print(f"[Supervisor] Jules accepted fix (task: {task_name})")
            return True
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"[Supervisor] Jules API error: {e.code} {error_body[:200]}")
        return False
    except Exception as e:
        print(f"[Supervisor] Jules API exception: {e}")
        return False


def check_all_agents_idle(lock_data):
    for agent_id, info in lock_data.get("agents", {}).items():
        if agent_id == "agent-7":
            continue
        status = info.get("status")
        if status in ("working", "assigned"):
            if not info.get("task_id"):
                return False
    return True


def trigger_dispatcher(token):
    repo = os.environ.get("GITHUB_REPOSITORY", "Koteyka371/ball-royale")
    url = f"https://api.github.com/repos/{repo}/actions/workflows/jules-dispatcher.yml/dispatches"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"token {token}",
    }
    payload = {"ref": "main"}

    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print("[Supervisor] Dispatcher triggered")
            return True
    except Exception as e:
        print(f"[Supervisor] Failed to trigger dispatcher: {e}")
        return False


def merge_pr(pr_number):
    print(f"[Supervisor] Merging PR #{pr_number}...")
    result = github_api(
        f"pulls/{pr_number}/merge",
        method="PUT",
        data={"merge_method": "squash"},
    )
    if result is None:
        return False
    return True


def get_open_prs():
    result = github_api("pulls?state=open&per_page=100")
    if result is None:
        return []
    return result


def get_task_for_pr(pr):
    title = pr.get("title", "")
    body = pr.get("body", "")
    task_id = ""
    if title.startswith("[") and "]" in title:
        task_id = title.split("]")[0].strip("[")
    elif body:
        for line in body.split("\n"):
            if line.startswith("Task:") or line.startswith("Task ID:"):
                task_id = line.split(":", 1)[1].strip()
                break
            if "task-" in line:
                idx = line.index("task-")
                end = idx
                while end < len(line) and line[end] not in " \n,;:)]}":
                    end += 1
                task_id = line[idx:end]
                break
    return task_id


def mark_task_done(task_id, agent_id):
    if not task_id:
        return

    try:
        tasks_data = load_json(TASK_FILE)
        for task in tasks_data.get("tasks", []):
            if task.get("id") == task_id:
                task["status"] = "done"
                break
        atomic_write_json(TASK_FILE, tasks_data)
        print(f"[Supervisor] Marked {task_id} as done in tasks file")
    except Exception as e:
        print(f"[Supervisor] Failed to mark task done: {e}")


def main():
    print("=" * 60)
    print("JULES SUPERVISOR (Agent 7)")
    print("=" * 60)

    if fcntl is None:
        print("[Supervisor] WARNING: fcntl not available, no file locking")

    lock_fd = open(SUPERVISOR_LOCK, "w")
    try:
        if fcntl:
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except (IOError, OSError):
                print("[Supervisor] Another supervisor is running, exiting")
                lock_fd.close()
                return 0
        else:
            lock_fd.close()

        if not git_pull():
            git_reset_to_remote()

        try:
            lock_data = load_json(LOCK_FILE)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[Supervisor] Failed to load {LOCK_FILE}: {e}")
            return 1

        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()

        updates = {"agents": {}}
        need_save = False

        # Reset stale agents
        for agent_id, agent_info in lock_data["agents"].items():
            if agent_id == "agent-7":
                continue

            status = agent_info.get("status")
            if status not in ("working", "assigned"):
                continue

            started = agent_info.get("started_at")
            if not started:
                continue

            try:
                start_dt = datetime.fromisoformat(started)
                if start_dt.tzinfo is None:
                    start_dt = start_dt.replace(tzinfo=timezone.utc)
                elapsed_min = (now - start_dt).total_seconds() / 60
            except (ValueError, TypeError):
                continue

            if elapsed_min > STALE_TIMEOUT_MIN:
                print(f"[Supervisor] {agent_id} stale ({elapsed_min:.0f} min), resetting")
                updates["agents"][agent_id] = {
                    "status": "idle",
                    "task_id": None,
                    "started_at": None,
                }
                need_save = True

        # Check if all agents idle → trigger dispatcher
        all_idle = check_all_agents_idle(lock_data)
        if all_idle:
            print("[Supervisor] All agents idle, triggering dispatcher...")
            token = os.environ.get("GITHUB_TOKEN", "")
            if token:
                trigger_dispatcher(token)
        else:
            working = [aid for aid, info in lock_data["agents"].items()
                       if aid != "agent-7" and info.get("status") in ("working", "assigned")]
            print(f"[Supervisor] Active agents: {', '.join(working)}")

        # Check open PRs and merge if CI passed
        print("\n[Supervisor] Checking open PRs...")
        prs = get_open_prs()
        if prs:
            for pr in prs:
                pr_num = pr["number"]
                pr_head = pr.get("head", {}).get("sha", "")
                labels = [l.get("name", "") for l in pr.get("labels", [])]
                is_automated = "automated" in labels

                print(f"\n  PR #{pr_num}: {pr.get('title', '?')[:50]}")
                print(f"    Labels: {labels}")
                print(f"    Mergeable: {pr.get('mergeable', '?')}")

                if not is_automated:
                    print(f"    Skipped (no 'automated' label)")
                    continue

                task_id = get_task_for_pr(pr)
                task_status = ""
                try:
                    tasks_data = load_json(TASK_FILE)
                    for task in tasks_data.get("tasks", []):
                        if task.get("id") == task_id:
                            task_status = task.get("status", "")
                            break
                except Exception:
                    pass

                if task_status == "done":
                    print(f"    Task {task_id} already done, merging immediately")
                    merge_pr(pr_num)
                    mark_task_done(task_id, "")
                    continue

                ci_status = get_ci_status(pr_head)

                if ci_status == "success":
                    print(f"    CI passed! Merging...")
                    if merge_pr(pr_num):
                        mark_task_done(task_id, "")
                elif ci_status == "failure":
                    print(f"    CI failed! Fixing via Jules API...")
                    jules_token = os.environ.get("JULES_API_KEY", "")
                    if jules_token:
                        agent_id = ""
                        if pr.get("user", {}).get("login", "").startswith("jules"):
                            branch = pr.get("head", {}).get("ref", "")
                            agent_id = branch.split("-agent-")[-1].split("-")[0] if "-agent-" in branch else ""
                            if agent_id and agent_id.isdigit():
                                agent_id = f"agent-{agent_id}"

                        agent_area = lock_data["agents"].get(agent_id, {}).get("area", "ai-core")
                        branch_name = pr.get("head", {}).get("ref", "")

                        fix_prompt = f"Fix CI failure for task {task_id}. Check the CI logs and fix the failing tests or code issues. Use branch '{branch_name}'."
                        invoke_jules(task_id, agent_area, fix_prompt, branch_name, jules_token)

                        for i in range(0, 15 * 60, 30):
                            new_ci = get_ci_status(pr_head)
                            if new_ci == "success":
                                print(f"    Fixed! Merging...")
                                merge_pr(pr_num)
                                mark_task_done(task_id, agent_id)
                                break
                            elif new_ci == "failure":
                                print(f"    Still failing ({i//60}m{i%60}s)")
                            time.sleep(30)
                else:
                    print(f"    CI pending...")
        else:
            print("[Supervisor] No open PRs")

        # Save and push
        if need_save:
            if save_and_push(updates, f"supervisor: update {len(updates['agents'])} agents"):
                print(f"\n[Supervisor] Saved {LOCK_FILE}")
            else:
                print("\n[Supervisor] FAILED to save")
        else:
            print("[Supervisor] No agent updates needed")

        print("\n[Supervisor] Done!")
        return 0

    finally:
        if fcntl:
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
            except Exception:
                pass
        lock_fd.close()


if __name__ == "__main__":
    sys.exit(main())
