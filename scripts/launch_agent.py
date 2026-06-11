#!/usr/bin/env python3
"""
Universal Jules Agent Launcher.
Usage: python launch_agent.py <agent_id>
Example: python launch_agent.py agent-1

Reads agent_lock.json to find assigned task, invokes Jules API, creates PR.
"""
import json
import sys
import os
import urllib.request
from datetime import datetime, timezone

LOCK_FILE = "agent_lock.json"
TASK_FILE = "agent_tasks.json"
MAX_CYCLES = 30

AGENT_PROMPTS = {
    "agent-1": {
        "name": "Jules Core",
        "focus": "AI core systems: BallBrain, Perception, Emotion, Decision, Action, Personality",
        "innovation": [
            "Emotional contagion (fear spreads between balls)",
            "Dynamic personality evolution based on battle experience",
            "Multi-layer threat assessment with memory",
            "Adaptive difficulty based on player behavior",
        ]
    },
    "agent-2": {
        "name": "Jules Behaviors",
        "focus": "AI behaviors: chase, flee, attack, kite, flank, group attack, collect booster",
        "innovation": [
            "Swarm intelligence (boid rules, flocking)",
            "Tactical positioning and formation behaviors",
            "Predictive movement (dodge, juke, zigzag)",
            "Territorial behavior (claim and defend areas)",
        ]
    },
    "agent-3": {
        "name": "Jules Tests",
        "focus": "Tests, ball type configs, quality assurance",
        "innovation": [
            "Stress tests for 1000+ balls",
            "Behavior coverage matrix",
            "Performance regression detection",
            "Battle simulation scenarios",
        ]
    },
    "agent-4": {
        "name": "Jules Content",
        "focus": "Game design docs, modes, arenas, content generation",
        "innovation": [
            "Procedural arena generation",
            "Dynamic event system (storms, power-ups)",
            "Loot table optimization",
            "Achievement and progression system",
        ]
    },
    "agent-5": {
        "name": "Jules Meta",
        "focus": "Workflows, scripts, automation, infrastructure",
        "innovation": [
            "Auto-scaling agent pool based on workload",
            "PR quality scoring system",
            "Automated code review pipeline",
            "Dependency update automation",
        ]
    },
    "agent-6": {
        "name": "Jules Innovation",
        "focus": "Experimental features: genetics, neural networks, new mechanics",
        "innovation": [
            "Ball genetics (offspring inherit traits, mutate)",
            "Neural network controlled balls that learn",
            "Ball relationships (rivalry, alliance, revenge)",
            "Physics chain reactions and environmental hazards",
        ]
    },
}


def load_json(path):
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_task_info(task_id, tasks_data):
    """Get full task info from agent_tasks.json."""
    for t in tasks_data.get("tasks", []):
        if t["id"] == task_id:
            return t
    return None


def build_prompt(agent_id, agent_config, task_info, lock_data):
    """Build the Jules prompt for this agent."""
    agent_meta = AGENT_PROMPTS.get(agent_id, {})
    task_title = task_info["title"]
    task_desc = task_info.get("description", "No description")

    # List what other agents are working on (to avoid conflicts)
    other_work = []
    for aid, ainfo in lock_data["agents"].items():
        if aid != agent_id and ainfo.get("status") == "working" and ainfo.get("task_id"):
            other_work.append(f"- {aid}: {ainfo['task_id']}")

    other_work_str = "\n".join(other_work) if other_work else "None"

    prompt = f"""You are {agent_meta.get('name', 'Jules')}, an autonomous AI developer.
You are working on Ball Royale — a 2D battle royale with AI-controlled balls.

## YOUR ROLE
Focus area: {agent_meta.get('focus', 'General development')}
Innovation priorities:
{chr(10).join('- ' + i for i in agent_meta.get('innovation', []))}

## CURRENT TASK
Title: {task_title}
Description: {task_desc}

## WHAT OTHER AGENTS ARE WORKING ON (DO NOT TOUCH THEIR FILES)
{other_work_str}

## YOUR RITUAL (every cycle)
1. RUN: git pull origin main
2. READ: AGENTS.md, docs/game_design.md, agent_tasks.json
3. READ: relevant source files for your area
4. WORK: Complete the current task with tests
5. EVOLVE: Fix bugs, improve code, invent new features (ONLY in your area)
6. VALIDATE: python3 tests/simulate_battle.py 100 && python3 scripts/quality_metrics.py
7. GENERATE: Add 3-5 new tasks to agent_tasks.json (only if < 100 total tasks).
   IMPORTANT: Each new task MUST have an "area" field matching one of:
   "ai-core", "behaviors", "tests", "content", "meta", "innovation"
   Set area based on what the task is about. The dispatcher uses this to assign tasks to agents.
8. COMMIT: git add -A && git commit -m "feat({agent_id}): {task_title}"
9. BRANCH: git checkout -b {agent_id}/{task_id}
10. PUSH: git push origin {agent_id}/{task_id}
11. PR: Create PR via GitHub API

## RULES
- ONLY modify files in your area
- NEVER touch files another agent is working on
- Fix anything broken even if not in the task
- Leave code better than you found it
- Be creative and bold
- If you see something cool in another agent's work, INSTEAD of touching it,
  generate a new task that builds upon it

## TASK FORMAT (when generating new tasks)
Each task in agent_tasks.json must have this structure:
```json
{
  "id": "unique-task-id",
  "status": "todo",
  "area": "ai-core|behaviors|tests|content|meta|innovation",
  "risk": "low|medium|high",
  "title": "Task title",
  "description": "What to do",
  "allowed_paths": ["src/ai/**"],
  "acceptance": ["Criteria 1", "Criteria 2"]
}
```
The "area" field is CRITICAL — it tells the dispatcher which agent should work on this task."""

    return prompt


def invoke_jules(api_key, prompt, title):
    """Invoke Jules API and return response."""
    payload = {
        "prompt": prompt,
        "sourceContext": {
            "source": "sources/github/Koteyka371/ball-royale",
            "githubRepoContext": {"startingBranch": "main"}
        },
        "automationMode": "AUTO_CREATE_PR",
        "title": title
    }

    url = "https://jules.googleapis.com/v1alpha/sessions"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")

    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def main():
    if len(sys.argv) < 2:
        print("Usage: python launch_agent.py <agent_id>")
        print("Example: python launch_agent.py agent-1")
        sys.exit(1)

    agent_id = sys.argv[1]
    valid_agents = [f"agent-{i}" for i in range(1, 7)]
    if agent_id not in valid_agents:
        print(f"ERROR: Invalid agent_id '{agent_id}'. Must be one of: {valid_agents}")
        sys.exit(1)

    # Load data
    lock_data = load_json(LOCK_FILE)
    tasks_data = load_json(TASK_FILE)

    agent_info = lock_data["agents"].get(agent_id)
    if not agent_info:
        print(f"ERROR: Agent {agent_id} not found in {LOCK_FILE}")
        sys.exit(1)

    # Check if agent has a task
    task_id = agent_info.get("task_id")
    if not task_id:
        print(f"[{agent_id}] No task assigned. Run dispatch_agents.py first.")
        sys.exit(0)

    # Check cycle limit
    if agent_info.get("cycles_today", 0) >= MAX_CYCLES:
        print(f"[{agent_id}] Daily limit reached ({MAX_CYCLES} cycles)")
        sys.exit(0)

    # Get task info
    task_info = get_task_info(task_id, tasks_data)
    if not task_info:
        print(f"[{agent_id}] Task {task_id} not found in {TASK_FILE}")
        sys.exit(1)

    print(f"[{agent_id}] Task: {task_id} — {task_info['title']}")

    # Get API key
    api_key_name = agent_info.get("api_key", "JULES_API_KEY")
    api_key = os.environ.get(api_key_name, "")
    if not api_key:
        print(f"ERROR: {api_key_name} is not set!")
        sys.exit(1)

    # Build prompt
    prompt = build_prompt(agent_id, agent_info, task_info, lock_data)

    # Mark as working
    lock_data["agents"][agent_id]["status"] = "working"
    lock_data["agents"][agent_id]["cycles_today"] = agent_info.get("cycles_today", 0) + 1
    lock_data["agents"][agent_id]["started_at"] = datetime.now(timezone.utc).isoformat()
    save_json(LOCK_FILE, lock_data)

    # Invoke Jules
    print(f"[{agent_id}] Invoking Jules API...")
    try:
        result = invoke_jules(api_key, prompt, f"Task: {task_info['title']}")
        print(f"[{agent_id}] Jules response: {result[:200]}")
        print(f"[{agent_id}] Invoked successfully!")
    except Exception as e:
        print(f"[{agent_id}] ERROR: {e}")
        # Reset status on failure
        lock_data["agents"][agent_id]["status"] = "idle"
        lock_data["agents"][agent_id]["task_id"] = None
        save_json(LOCK_FILE, lock_data)
        sys.exit(1)


if __name__ == "__main__":
    main()
