#!/usr/bin/env python3
"""
Jules Supervisor — monitors and fixes the agent system.
Runs every 15 minutes via GitHub Actions.
Checks agents, PRs, tasks. Fixes problems. Calls Jules API if code needs fixing.
"""
import json
import os
import subprocess
import urllib.request
import time
from datetime import datetime, timezone

LOCK_FILE = "agent_lock.json"
TASK_FILE = "agent_tasks.json"
REPO = "Koteyka371/ball-royale"
STALE_TIMEOUT_MIN = 30


def load_json(path):
    with open(path) as f:
        return json.load(f)


def git_pull():
    subprocess.run(
        ["git", "pull", "origin", "main", "--no-edit"],
        capture_output=True, text=True, timeout=30
    )


def save_and_push(lock_data, message):
    with open(LOCK_FILE, "w") as f:
        json.dump(lock_data, f, indent=2, ensure_ascii=False)
    subprocess.run(["git", "add", LOCK_FILE], capture_output=True, timeout=10)
    subprocess.run(["git", "commit", "-m", message], capture_output=True, timeout=10)
    result = subprocess.run(
        ["git", "push", "origin", "main"],
        capture_output=True, text=True, timeout=30
    )
    return result.returncode == 0


def github_get(path):
    token = os.environ.get("GITHUB_TOKEN", "")
    url = f"https://api.github.com/repos/{REPO}{path}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    if token:
        headers["Authorization"] = f"token {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def github_request(path, method="GET", data=None):
    token = os.environ.get("GITHUB_TOKEN", "")
    url = f"https://api.github.com/repos/{REPO}{path}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
    }
    if token:
        headers["Authorization"] = f"token {token}"

    data_bytes = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"[Supervisor] GitHub API error {e.code}: {body[:200]}")
        return None


def check_agents_status(lock_data):
    now = datetime.now(timezone.utc)
    problems = []
    actions = []

    for agent_id, info in lock_data["agents"].items():
        status = info.get("status")
        started = info.get("started_at")
        task_id = info.get("task_id")
        cycles = info.get("cycles_today", 0)

        if status in ("assigned", "working") and started:
            elapsed = (now - datetime.fromisoformat(started)).total_seconds() / 60
            if elapsed > STALE_TIMEOUT_MIN:
                problems.append(f"{agent_id}: STALE after {elapsed:.0f} min (status={status})")
                actions.append({
                    "type": "reset_agent",
                    "agent_id": agent_id,
                    "reason": f"stale after {elapsed:.0f} min"
                })

        if status == "idle" and task_id:
            problems.append(f"{agent_id}: idle but has task {task_id}")
            actions.append({
                "type": "clear_task",
                "agent_id": agent_id,
                "reason": "idle with assigned task"
            })

        if cycles >= 30:
            problems.append(f"{agent_id}: reached daily limit ({cycles}/30)")

    return problems, actions


def check_open_prs():
    problems = []
    actions = []

    try:
        prs = github_get("/pulls?state=open&per_page=30")
    except Exception as e:
        print(f"[Supervisor] Failed to fetch PRs: {e}")
        return problems, actions

    if not prs:
        return problems, actions

    for pr in prs:
        pr_number = pr["number"]
        title = pr.get("title", "")
        labels = [l["name"] for l in pr.get("labels", [])]
        mergeable = pr.get("mergeable")
        author = pr.get("user", {}).get("login", "")

        if author == "google-labs-jules[bot]" or "automated" in labels:
            if "automated" not in labels:
                problems.append(f"PR #{pr_number}: Jules PR without 'automated' label")
                actions.append({
                    "type": "add_label",
                    "pr_number": pr_number,
                    "label": "automated"
                })

            if mergeable == "MERGEABLE" and "automated" in labels:
                problems.append(f"PR #{pr_number}: ready to merge ({title[:50]})")
                actions.append({
                    "type": "merge_pr",
                    "pr_number": pr_number
                })

            ci_status = get_ci_status(pr_number)
            if ci_status == "failure":
                problems.append(f"PR #{pr_number}: CI FAILED ({title[:50]})")
                actions.append({
                    "type": "fix_code",
                    "pr_number": pr_number,
                    "title": title,
                    "head_ref": pr.get("head", {}).get("ref", ""),
                    "reason": "CI failed"
                })

    return problems, actions


def get_ci_status(pr_number):
    try:
        commits = github_get(f"/pulls/{pr_number}/commits?per_page=1")
        if commits:
            sha = commits[0]["sha"]
            status_data = github_get(f"/commits/{sha}/status")
            if status_data:
                return status_data.get("state", "pending")

            check_runs = github_get(f"/commits/{sha}/check-runs?per_page=1")
            if check_runs and check_runs.get("total_count", 0) > 0:
                all_passed = all(
                    cr.get("conclusion") == "success"
                    for cr in check_runs.get("check_runs", [])
                )
                any_failed = any(
                    cr.get("conclusion") == "failure"
                    for cr in check_runs.get("check_runs", [])
                )
                if any_failed:
                    return "failure"
                if all_passed:
                    return "success"
    except Exception as e:
        print(f"[Supervisor] CI check error for PR #{pr_number}: {e}")
    return "pending"


def check_task_health(lock_data, tasks_data):
    problems = []
    actions = []

    todo_tasks = [t for t in tasks_data.get("tasks", []) if t.get("status") == "todo"]
    done_tasks = [t for t in tasks_data.get("tasks", []) if t.get("status") == "done"]

    if len(todo_tasks) < 5:
        problems.append(f"Low task pool: {len(todo_tasks)} todo / {len(done_tasks)} done / {len(tasks_data.get('tasks', []))} total")

    for agent_id, info in lock_data["agents"].items():
        task_id = info.get("task_id")
        if task_id and info.get("status") == "idle":
            task_found = any(t["id"] == task_id for t in tasks_data.get("tasks", []))
            if task_found:
                problems.append(f"{agent_id}: idle but task '{task_id}' still assigned")
                actions.append({
                    "type": "unassign_task",
                    "agent_id": agent_id,
                    "task_id": task_id
                })

    return problems, actions


def check_all_agents_idle(lock_data):
    active_agents = [
        aid for aid, info in lock_data["agents"].items()
        if info.get("status") in ("working", "assigned")
    ]

    if len(active_agents) == 0:
        tasks_data = load_json(TASK_FILE)
        todo_count = len([t for t in tasks_data["tasks"] if t.get("status") == "todo"])
        if todo_count > 0:
            return True, f"All agents idle, {todo_count} tasks available"
        else:
            return False, "All agents idle but no tasks"

    return False, f"{len(active_agents)} agents active"


def reset_agent(agent_id):
    git_pull()
    lock_data = load_json(LOCK_FILE)
    if agent_id in lock_data["agents"]:
        lock_data["agents"][agent_id]["status"] = "idle"
        lock_data["agents"][agent_id]["task_id"] = None
        lock_data["agents"][agent_id]["started_at"] = None
        save_and_push(lock_data, f"supervisor: reset stale {agent_id}")
        print(f"[Supervisor] Reset {agent_id}")


def clear_agent_task(agent_id):
    git_pull()
    lock_data = load_json(LOCK_FILE)
    if agent_id in lock_data["agents"]:
        lock_data["agents"][agent_id]["task_id"] = None
        lock_data["agents"][agent_id]["status"] = "idle"
        save_and_push(lock_data, f"supervisor: clear task for {agent_id}")
        print(f"[Supervisor] Cleared task for {agent_id}")


def merge_pr(pr_number):
    result = github_request(f"/pulls/{pr_number}/merge", method="PUT", data={
        "merge_method": "squash"
    })
    if result is not None:
        print(f"[Supervisor] Merged PR #{pr_number}")
        return True
    return False


def add_label_to_pr(pr_number, label):
    result = github_request(f"/issues/{pr_number}/labels", method="POST", data={
        "labels": [label]
    })
    if result is not None:
        print(f"[Supervisor] Added label '{label}' to PR #{pr_number}")
        return True
    return False


def unassign_task(agent_id, task_id):
    git_pull()
    lock_data = load_json(LOCK_FILE)
    if agent_id in lock_data["agents"]:
        lock_data["agents"][agent_id]["task_id"] = None
        lock_data["agents"][agent_id]["status"] = "idle"
        save_and_push(lock_data, f"supervisor: unassign {task_id} from {agent_id}")
        print(f"[Supervisor] Unassigned {task_id} from {agent_id}")


def trigger_dispatcher():
    result = github_request(
        "/actions/workflows/jules-dispatcher.yml/dispatches",
        method="POST",
        data={"ref": "main"}
    )
    if result is not None:
        print("[Supervisor] Triggered dispatcher")
        return True
    return False


def fix_code_via_jules(pr_number, title, head_ref):
    api_key = os.environ.get("JULES_API_KEY")
    if not api_key:
        print(f"[Supervisor] No JULES_API_KEY, cannot fix PR #{pr_number}")
        return False

    prompt = f"""You are Jules Supervisor, fixing a broken PR.

## CURRENT PR
Number: #{pr_number}
Title: {title}
Branch: {head_ref}

## PROBLEM
CI checks failed on this PR. You need to fix the failing tests or code.

## YOUR TASK
1. git pull origin main
2. Read the failing code
3. Fix the issue
4. Run: pytest tests/ -v
5. Commit and push to the branch: {head_ref}

## RULES
- Only fix what's broken
- Don't change unrelated code
- Keep the same code style
- Make sure all tests pass before committing
"""

    payload = {
        "prompt": prompt,
        "sourceContext": {
            "source": f"sources/github/{REPO}",
            "githubRepoContext": {
                "startingBranch": head_ref or "main"
            }
        },
        "automationMode": "AUTO_CREATE_PR",
        "title": f"Fix: {title}"
    }

    url = "https://jules.googleapis.com/v1alpha/sessions"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }

    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = resp.read().decode("utf-8")
            print(f"[Supervisor] Jules invoked to fix PR #{pr_number}")
            return True
    except Exception as e:
        print(f"[Supervisor] Failed to invoke Jules for PR #{pr_number}: {e}")
        return False


def execute_actions(actions):
    for action in actions:
        action_type = action["type"]

        if action_type == "reset_agent":
            reset_agent(action["agent_id"])

        elif action_type == "clear_task":
            clear_agent_task(action["agent_id"])

        elif action_type == "merge_pr":
            merge_pr(action["pr_number"])

        elif action_type == "add_label":
            add_label_to_pr(action["pr_number"], action["label"])

        elif action_type == "fix_code":
            fix_code_via_jules(
                action["pr_number"],
                action["title"],
                action.get("head_ref", "")
            )

        elif action_type == "unassign_task":
            unassign_task(action["agent_id"], action["task_id"])

        elif action_type == "trigger_dispatcher":
            trigger_dispatcher()

        time.sleep(1)


def main():
    print("=" * 60)
    print("JULES SUPERVISOR")
    print(f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)

    git_pull()

    lock_data = load_json(LOCK_FILE)
    tasks_data = load_json(TASK_FILE)

    all_problems = []
    all_actions = []

    print("\n[1] Checking agents...")
    problems, actions = check_agents_status(lock_data)
    all_problems.extend(problems)
    all_actions.extend(actions)

    print("\n[2] Checking open PRs...")
    problems, actions = check_open_prs()
    all_problems.extend(problems)
    all_actions.extend(actions)

    print("\n[3] Checking task health...")
    problems, actions = check_task_health(lock_data, tasks_data)
    all_problems.extend(problems)
    all_actions.extend(actions)

    print("\n[4] Checking if dispatcher needed...")
    need_dispatch, reason = check_all_agents_idle(lock_data)
    if need_dispatch:
        all_actions.append({"type": "trigger_dispatcher"})
        all_problems.append(reason)

    print("\n" + "=" * 60)
    print("REPORT")
    print("=" * 60)
    if all_problems:
        print(f"\nProblems found ({len(all_problems)}):")
        for p in all_problems:
            print(f"  - {p}")
    else:
        print("\nNo problems found!")

    print(f"\nActions to take: {len(all_actions)}")

    if all_actions:
        print("\nExecuting actions...")
        execute_actions(all_actions)
    else:
        print("Nothing to do.")

    tasks_todo = len([t for t in tasks_data["tasks"] if t.get("status") == "todo"])
    tasks_done = len([t for t in tasks_data["tasks"] if t.get("status") == "done"])
    active = sum(1 for a in lock_data["agents"].values() if a.get("status") in ("working", "assigned"))
    total_cycles = sum(a.get("cycles_today", 0) for a in lock_data["agents"].values())

    print(f"\n{'='*60}")
    print("STATUS")
    print(f"{'='*60}")
    print(f"  Tasks: {tasks_todo} todo / {tasks_done} done")
    print(f"  Active agents: {active}/6")
    print(f"  Cycles today: {total_cycles}/180")

    print("\n[Supervisor] Done!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
