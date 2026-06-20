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
import tempfile
from datetime import datetime, timezone

try:
    import fcntl
except ImportError:
    fcntl = None

LOCK_FILE = "agent_lock.json"
TASK_FILE = "agent_tasks.json"
SUPERVISOR_LOCK = ".supervisor.lock"
MAX_RETRIES = 5
STALE_TIMEOUT_MIN = 45
SUPERVISOR_ID = "supervisor"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


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
        print(f"[Supervisor] git pull failed: {result.stderr}")
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
        print(f"[Supervisor] git add failed: {add_result.stderr}")
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
        print("[Supervisor] verify_pushed: git log failed, cannot verify")
        return False
    return len(result.stdout.strip()) == 0


def save_and_push(new_data, message):
    if not new_data.get("agents"):
        return True

    for attempt in range(MAX_RETRIES):
        if not git_pull():
            if not git_reset_to_remote():
                print("[Supervisor] Cannot sync with remote, aborting")
                return False

        try:
            with open(LOCK_FILE, encoding="utf-8") as f:
                current = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, PermissionError, UnicodeDecodeError) as e:
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
            print("[Supervisor] Commit OK but push verify failed, retrying...")
        else:
            print(f"[Supervisor] Push failed ({attempt + 1}/{MAX_RETRIES})")
        time.sleep(2)

    print(f"[Supervisor] ERROR: Failed after {MAX_RETRIES} retries")
    return False


def github_api(endpoint, method="GET", data=None, token=None, _retry_count=0):
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
            return json.loads(content) if content.strip() else None
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        if e.code == 403 and "rate limit" in error_body.lower() and _retry_count < 3:
            wait_time = 60 * (_retry_count + 1)
            print(f"[Supervisor] Rate limited, waiting {wait_time}s (retry {_retry_count + 1}/3)...")
            time.sleep(wait_time)
            return github_api(endpoint, method, data, token, _retry_count + 1)
        print(f"[Supervisor] API {method} {endpoint}: {e.code} {error_body[:300]}")
        return None
    except Exception as e:
        print(f"[Supervisor] API error: {e}")
        return None


def get_ci_status(sha):
    if not sha:
        return "pending"
    token = os.environ.get("GITHUB_TOKEN", "")

    repo = os.environ.get("GITHUB_REPOSITORY", "Koteyka371/ball-royale")
    all_check_runs = []
    page = 1

    while True:
        url = f"https://api.github.com/repos/{repo}/commits/{sha}/check-runs?per_page=100&page={page}"
        req = urllib.request.Request(url, headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        })

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 401 or e.code == 403:
                print(f"[Supervisor] CI status check auth error: {e.code}")
                return "error"
            return "pending"
        except Exception:
            return "pending"

        runs = data.get("check_runs", [])
        all_check_runs.extend(runs)

        if len(runs) < 100 or page >= 10:
            break
        page += 1

    if not all_check_runs:
        return "pending"

    blocking_conclusions = {"failure", "timed_out", "cancelled", "action_required"}
    has_failure = False
    all_completed = True
    has_validation_run = False

    for run in all_check_runs:
        name = run.get("name", "")
        # Only care about the validation suite check-runs
        if "validate" not in name.lower() and "ci validation" not in name.lower():
            continue

        has_validation_run = True
        conclusion = run.get("conclusion")
        status = run.get("status", "")
        if conclusion in blocking_conclusions:
            has_failure = True
        if status != "completed":
            all_completed = False

    if not has_validation_run:
        return "pending"
    if has_failure:
        return "failure"
    if not all_completed:
        return "pending"
    return "success"


def invoke_jules(task_id, area, prompt, branch_name, token):
    if not token:
        token = os.environ.get("JULES_API_KEY", "")
    if not token:
        print("[Supervisor] No Jules token available")
        return False

    repo = os.environ.get('GITHUB_REPOSITORY', 'Koteyka371/ball-royale')
    full_prompt = (
        f"Project: Ball Royale — 2D battle royale with AI-controlled balls.\n\n"
        f"AREA: {area}\n"
        f"TASK: {prompt}\n\n"
        f"BRANCH: Use existing branch '{branch_name}' for your changes.\n\n"
        f"RULES:\n"
        f"1. Work ONLY on branch '{branch_name}'\n"
        f"2. Commit with clear messages\n"
        f"3. Push branch when done\n"
        f"4. DO NOT modify files outside src/\n"
        f"5. Fix the failing tests or code issues\n"
    )

    url = "https://jules.googleapis.com/v1alpha/sessions"
    headers = {
        "x-goog-api-key": token,
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": full_prompt,
        "title": f"[{task_id}] CI fix - {area}",
        "sourceContext": {
            "source": f"sources/github/{repo}",
            "githubRepoContext": {
                "startingBranch": branch_name
            }
        },
        "requirePlanApproval": False,
        "automationMode": "AUTO_CREATE_PR",
    }

    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            session_name = body.get("name", "")
            print(f"[Supervisor] Jules accepted fix (session: {session_name})")
            return True
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"[Supervisor] Jules API error: {e.code} {error_body[:300]}")
        return False
    except Exception as e:
        print(f"[Supervisor] Jules API exception: {e}")
        return False


def find_agent_by_task_id(lock_data, task_id):
    if not task_id:
        return ""
    for agent_id, info in lock_data.get("agents", {}).items():
        if agent_id == SUPERVISOR_ID:
            continue
        if isinstance(info, dict) and info.get("task_id") == task_id:
            return agent_id
    return ""


def check_all_agents_idle(lock_data):
    for agent_id, info in lock_data.get("agents", {}).items():
        if agent_id == SUPERVISOR_ID:
            continue
        if not isinstance(info, dict):
            continue
        status = info.get("status")
        if status in ("working", "assigned"):
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


def merge_pr(pr_number, branch_name="", mergeable=None):
    if mergeable is False:
        print(f"[Supervisor] PR #{pr_number} has conflicts, skipping merge")
        return False
    print(f"[Supervisor] Merging PR #{pr_number}...")
    result = github_api(
        f"pulls/{pr_number}/merge",
        method="PUT",
        data={"merge_method": "squash"},
    )
    if result is None:
        return False
    if result.get("merged") is not True:
        print(f"[Supervisor] Merge response says not merged: {result.get('message', '')}")
        return False
    
    if branch_name and branch_name not in ("main", "master"):
        print(f"[Supervisor] Deleting merged branch '{branch_name}'...")
        github_api(f"git/refs/heads/{branch_name}", method="DELETE")
        
    return True


def get_open_prs():
    result = github_api("pulls?state=open&per_page=100")
    if result is None:
        return []
    if isinstance(result, dict):
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
    if not task_id:
        print(f"[Supervisor] WARNING: Could not parse task_id from PR #{pr.get('number')}: {title[:60]}")
    return task_id


def update_changelog(task_id, title, description):
    changelog_path = "docs/agent_changelog.md"
    os.makedirs(os.path.dirname(changelog_path), exist_ok=True)
    
    header = ""
    if not os.path.exists(changelog_path):
        header = "# Ball Royale — Agent Changelog\n\nTracked history of successful tasks completed by autonomous agents.\n\n"
        
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    entry = f"## [{task_id}] {title} — *{date_str}*\n\n{description}\n\n---\n\n"
    
    existing = ""
    if os.path.exists(changelog_path):
        with open(changelog_path, "r", encoding="utf-8") as f:
            existing = f.read()
            
    new_content = ""
    if existing.startswith("# Ball Royale — Agent Changelog"):
        idx = existing.find("##")
        if idx != -1:
            new_content = existing[:idx] + entry + existing[idx:]
        else:
            new_content = existing.strip() + "\n\n" + entry
    else:
        new_content = header + entry + existing
        
    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"[Supervisor] Appended task {task_id} to {changelog_path}")


def mark_task_done(task_id):
    if not task_id:
        return

    try:
        git_pull()

        tasks_data = load_json(TASK_FILE)
        found = False
        task_obj = None
        for task in tasks_data.get("tasks", []):
            if task.get("id") == task_id:
                task["status"] = "done"
                task_obj = task
                found = True
                break
        if not found:
            print(f"[Supervisor] WARNING: Task {task_id} not found in tasks file")
            return
            
        atomic_write_json(TASK_FILE, tasks_data)
        print(f"[Supervisor] Marked {task_id} as done in tasks file")

        # Update the agent changelog
        if task_obj:
            try:
                update_changelog(task_id, task_obj.get("title", f"Task {task_id}"), task_obj.get("description", ""))
            except Exception as e:
                print(f"[Supervisor] WARNING: Failed to update changelog: {e}")

        subprocess.run(["git", "add", TASK_FILE], capture_output=True, timeout=10)
        subprocess.run(["git", "add", "docs/agent_changelog.md"], capture_output=True, timeout=10)
        
        diff_result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            capture_output=True, timeout=10
        )
        if diff_result.returncode != 0:
            commit_result = subprocess.run(
                ["git", "commit", "-m", f"supervisor: mark {task_id} done"],
                capture_output=True, text=True, timeout=10
            )
            if commit_result.returncode == 0:
                for attempt in range(3):
                    push_result = subprocess.run(
                        ["git", "push", "origin", "main"],
                        capture_output=True, text=True, timeout=30
                    )
                    if push_result.returncode == 0:
                        print("[Supervisor] Committed task status update and changelog")
                        break
                    print(f"[Supervisor] Push failed (attempt {attempt + 1}/3): {push_result.stderr}")
                    time.sleep(2)
                else:
                    print("[Supervisor] Failed to push task status after 3 attempts")
            else:
                print(f"[Supervisor] Failed to commit task status: {commit_result.stderr}")
    except Exception as e:
        print(f"[Supervisor] Failed to mark task done: {e}")


def reset_stale_agents(lock_data, now):
    stale_resets = {}
    agents = lock_data.get("agents", {})
    if not isinstance(agents, dict):
        return stale_resets

    for agent_id, agent_info in agents.items():
        if agent_id == SUPERVISOR_ID:
            continue
        if not isinstance(agent_info, dict):
            continue

        status = agent_info.get("status")
        if status not in ("working", "assigned"):
            continue

        started = agent_info.get("started_at")
        if not started:
            stale_resets[agent_id] = {
                "status": "idle",
                "task_id": None,
                "started_at": None,
            }
            continue

        try:
            start_dt = datetime.fromisoformat(started)
            if start_dt.tzinfo is None:
                start_dt = start_dt.replace(tzinfo=timezone.utc)
            elapsed_min = (now - start_dt).total_seconds() / 60
        except (ValueError, TypeError):
            stale_resets[agent_id] = {
                "status": "idle",
                "task_id": None,
                "started_at": None,
            }
            continue

        if elapsed_min > STALE_TIMEOUT_MIN:
            print(f"[Supervisor] {agent_id} stale ({elapsed_min:.0f} min), resetting")
            stale_resets[agent_id] = {
                "status": "idle",
                "task_id": None,
                "started_at": None,
            }

    return stale_resets


def main():
    print("=" * 60)
    print("JULES SUPERVISOR (Agent 7)")
    print("=" * 60)

    if fcntl is None:
        print("[Supervisor] WARNING: fcntl not available, no file locking")

    lock_fd = None
    try:
        lock_fd = open(SUPERVISOR_LOCK, "w")
        if fcntl:
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except (IOError, OSError):
                print("[Supervisor] Another supervisor is running, exiting")
                lock_fd.close()
                lock_fd = None
                return 0
        else:
            lock_fd.close()
            lock_fd = None

        if not git_pull():
            if not git_reset_to_remote():
                print("[Supervisor] Cannot sync with remote, aborting")
                return 1

        try:
            lock_data = load_json(LOCK_FILE)
        except (FileNotFoundError, json.JSONDecodeError, PermissionError, UnicodeDecodeError) as e:
            print(f"[Supervisor] Failed to load {LOCK_FILE}: {e}")
            return 1

        now = datetime.now(timezone.utc)

        stale_resets = reset_stale_agents(lock_data, now)

        for agent_id, reset_data in stale_resets.items():
            if agent_id in lock_data.get("agents", {}):
                lock_data["agents"][agent_id] = {
                    **lock_data["agents"][agent_id],
                    **reset_data,
                }

        updates = {"agents": {}}
        need_save = False

        for agent_id, reset_data in stale_resets.items():
            updates["agents"][agent_id] = lock_data["agents"][agent_id]
            need_save = True

        if need_save:
            if not save_and_push(updates, f"supervisor: reset {len(updates['agents'])} stale agents"):
                print("[Supervisor] FAILED to save stale resets")

        lock_data = load_json(LOCK_FILE)

        all_idle = check_all_agents_idle(lock_data)

        if all_idle:
            try:
                tasks_data = load_json(TASK_FILE)
                todo_count = sum(1 for t in tasks_data.get("tasks", []) if t.get("status") == "todo")
            except Exception:
                todo_count = 0
            if todo_count > 0:
                print(f"[Supervisor] All agents idle, {todo_count} tasks remaining, triggering dispatcher...")
                token = os.environ.get("GITHUB_TOKEN", "")
                if token:
                    trigger_dispatcher(token)
            else:
                print("[Supervisor] All agents idle, no tasks remaining")
        else:
            working = [aid for aid, info in lock_data.get("agents", {}).items()
                       if aid != SUPERVISOR_ID and isinstance(info, dict)
                       and info.get("status") in ("working", "assigned")]
            print(f"[Supervisor] Active agents: {', '.join(working)}")

        print("\n[Supervisor] Checking open PRs...")
        prs = get_open_prs()
        pr_updates = {"agents": {}}
        pr_need_save = False

        if prs:
            for pr in prs:
                pr_num = pr.get("number")
                pr_head = pr.get("head", {}).get("sha", "")
                labels = [l.get("name", "") for l in pr.get("labels", [])]
                task_id = get_task_for_pr(pr)
                is_automated = "automated" in labels or bool(task_id)

                print(f"\n  PR #{pr_num}: {pr.get('title', '?')[:50]}")
                print(f"    Labels: {labels}")
                print(f"    Mergeable: {pr.get('mergeable', '?')}")

                if not is_automated:
                    print("    Skipped (no 'automated' label and no task_id)")
                    continue
                
                if task_id == "Auto":
                    print("    Auto PR detected! Merging immediately to propagate tasks to main.")
                    branch_name = pr.get("head", {}).get("ref", "")
                    merge_pr(pr_num, branch_name=branch_name)
                    continue

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
                    print(f"    Task {task_id} already done, CLOSING duplicate PR immediately")
                    branch_name = pr.get("head", {}).get("ref", "")
                    
                    # Close the PR via API
                    token = os.environ.get("GITHUB_TOKEN", "")
                    repo = os.environ.get("GITHUB_REPOSITORY", "Koteyka371/ball-royale")
                    try:
                        url = f"https://api.github.com/repos/{repo}/pulls/{pr_num}"
                        data = json.dumps({"state": "closed"}).encode("utf-8")
                        req = urllib.request.Request(url, data=data, headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}, method="PATCH")
                        urllib.request.urlopen(req, timeout=15)
                        
                        # Also delete the branch
                        if branch_name:
                            subprocess.run(["git", "push", "origin", "--delete", branch_name], capture_output=True)
                    except Exception as e:
                        print(f"    Failed to close PR #{pr_num}: {e}")
                        
                    if True: # simulate success block
                        pr_need_save = True
                        agent_id_for_pr = find_agent_by_task_id(lock_data, task_id)
                        if agent_id_for_pr:
                            pr_updates["agents"][agent_id_for_pr] = {
                                "status": "idle",
                                "task_id": None,
                                "started_at": None,
                            }
                    continue

                ci_status = get_ci_status(pr_head)

                if ci_status == "success":
                    print("    CI passed! Merging...")
                    branch_name = pr.get("head", {}).get("ref", "")
                    if merge_pr(pr_num, branch_name=branch_name):
                        mark_task_done(task_id)
                        pr_need_save = True
                        agent_id_for_pr = find_agent_by_task_id(lock_data, task_id)
                        if agent_id_for_pr:
                            pr_updates["agents"][agent_id_for_pr] = {
                                "status": "idle",
                                "task_id": None,
                                "started_at": None,
                            }
                elif ci_status == "failure":
                    print("    CI failed! Fixing via Jules API...")
                    branch_name = pr.get("head", {}).get("ref", "")
                    agent_id = find_agent_by_task_id(lock_data, task_id)

                    if not agent_id:
                        print(f"    Could not find agent for task '{task_id}', skipping CI fix")
                        continue

                    # Determine primary and fallback token based on agent number
                    agent_num = 1
                    try:
                        agent_num = int(agent_id.split("-")[1])
                    except (IndexError, ValueError):
                        pass

                    token_env = "JULES_API_KEY_2" if agent_num % 2 == 0 else "JULES_API_KEY"
                    jules_token = os.environ.get(token_env, "")
                    if not jules_token:
                        fallback_env = "JULES_API_KEY" if token_env == "JULES_API_KEY_2" else "JULES_API_KEY_2"
                        jules_token = os.environ.get(fallback_env, "")
                        if jules_token:
                            print(f"[Supervisor] Primary {token_env} missing, using fallback {fallback_env} for {agent_id}")

                    if jules_token:
                        agent_area = lock_data.get("agents", {}).get(agent_id, {}).get("area", "ai-core")

                        fix_prompt = (
                            f"Fix CI failure for task {task_id}. Check the CI logs "
                            f"and fix the failing tests or code issues. "
                            f"Use branch '{branch_name}'."
                        )
                        if invoke_jules(task_id, agent_area, fix_prompt, branch_name, jules_token):
                            consecutive_failures = 0
                            for i in range(0, 15 * 60, 30):
                                try:
                                    pr_data = github_api(
                                        f"pulls/{pr_num}",
                                        token=os.environ.get("GITHUB_TOKEN", "")
                                    )
                                    if pr_data:
                                        new_head = pr_data.get("head", {}).get("sha", "")
                                        if new_head and new_head != pr_head:
                                            pr_head = new_head
                                            print(f"[Supervisor] PR head updated to {pr_head[:8]}")
                                except Exception:
                                    pass

                                new_ci = get_ci_status(pr_head)
                                elapsed = (i + 30) // 60
                                print(f"[Supervisor] CI status ({elapsed}m): {new_ci}")

                                if new_ci == "success":
                                    print("    Fixed! Merging...")
                                    target_branch = pr_data.get("head", {}).get("ref", "") if pr_data else branch_name
                                    if merge_pr(pr_num, branch_name=target_branch, mergeable=pr_data.get("mergeable") if pr_data else None):
                                        mark_task_done(task_id)
                                        pr_need_save = True
                                        pr_updates["agents"][agent_id] = {
                                            "status": "idle",
                                            "task_id": None,
                                            "started_at": None,
                                        }
                                    break
                                elif new_ci == "failure":
                                    consecutive_failures += 1
                                    if consecutive_failures >= 3:
                                        print(f"    Still failing after {consecutive_failures} checks, giving up")
                                        break
                                    print(f"    Still failing ({elapsed}m)")
                                elif new_ci == "pending":
                                    consecutive_failures = 0
                                elif new_ci == "error":
                                    print("    CI auth error, aborting fix loop")
                                    break

                                if i + 30 < 15 * 60:
                                    time.sleep(30)
                        else:
                            print(f"    Jules API failed to trigger fix for {agent_id}")
                            if agent_id:
                                pr_updates["agents"][agent_id] = {
                                    "status": "idle",
                                    "task_id": None,
                                    "started_at": None,
                                }
                                pr_need_save = True
                else:
                    if ci_status == "error":
                        print("    CI auth error, skipping this PR")
                    else:
                        print("    CI pending...")
        else:
            print("[Supervisor] No open PRs")

        if pr_need_save and pr_updates.get("agents"):
            if save_and_push(pr_updates, "supervisor: PR updates"):
                print(f"\n[Supervisor] Saved {LOCK_FILE}")
            else:
                print("\n[Supervisor] FAILED to save PR updates")
        else:
            print("[Supervisor] No PR updates needed")

        print("\n[Supervisor] Done!")
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
