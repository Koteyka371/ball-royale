#!/usr/bin/env python3
"""Jules Session Launcher #2 — reads SECOND task and invokes Jules API."""
import json
import sys
import os
import urllib.request

def main():
    api_key = os.environ.get("JULES_API_KEY", "")
    if not api_key:
        print("ERROR: JULES_API_KEY is not set!")
        sys.exit(1)

    # Read SECOND task (not the first one — Jules #1 takes the first)
    try:
        with open("agent_tasks.json") as f:
            data = json.load(f)
        tasks = [t for t in data.get("tasks", []) if t.get("status") == "todo"]
        if len(tasks) >= 2:
            task = tasks[1]  # Second task
            title = task["title"]
            desc = task.get("description", "No description")
        elif tasks:
            task = tasks[0]
            title = task["title"]
            desc = task.get("description", "No description")
        else:
            title = "Improve the project"
            desc = "No tasks left - improve everything"
    except Exception as e:
        print(f"Error reading tasks: {e}")
        title = "Improve the project"
        desc = "Fix any issues found"

    print(f"Task: {title}")

    prompt = f"""You are Jules (Instance #2), an autonomous AI developer.
You are the CO-CREATOR of Ball Royale — a 2D battle royale with AI-controlled balls.

## CURRENT TASK
Title: {title}
Description: {desc}

## YOUR MISSION
You work in PARALLEL with Jules #1. He takes odd tasks, you take even tasks.
Do NOT work on the same file as Jules #1.

## SYNCHRONIZATION
- Jules #1 works FIRST and merges his PR
- You start 10 minutes AFTER him
- By the time you start, his PR is already merged
- Check git log to see what he changed — do NOT touch the same files
- Pick a DIFFERENT task and work on DIFFERENT files

## YOUR RITUAL (every cycle)
1. RUN: git pull origin main (get latest changes from Jules #1)
2. READ: AGENTS.md, docs/game_design.md, agent_tasks.json, src/, tests/, scripts/, configs/
3. WORK: Complete the current task with tests (different files than Jules #1)
4. EVOLVE: Fix bugs, improve code, invent new features
5. VALIDATE: python3 tests/simulate_battle.py 100 && python3 scripts/quality_metrics.py
6. GENERATE: Add 3-5 new tasks to agent_tasks.json
7. PR: Include everything — task + fixes + improvements + new tasks

## INNOVATION PRIORITIES
- Swarm intelligence (boid rules, flocking)
- Ball genetics (offspring inherit traits, mutate)
- Neural network controlled balls
- Emotional contagion (fear spreads between balls)
- AI battle commentator
- Ball relationships (rivalry, alliance, revenge)
- Procedural arena generation
- Physics chain reactions

## RULES
- Fix anything broken even if not in the task
- Leave code better than you found it
- Be creative and bold
- Generate new tasks so the next cycle has work"""

    payload = {
        "prompt": prompt,
        "sourceContext": {
            "source": "sources/github/Koteyka371/ball-royale",
            "githubRepoContext": {"startingBranch": "main"}
        },
        "automationMode": "AUTO_CREATE_PR",
        "title": f"Task #2: {title}"
    }

    # Send to Jules API
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
            print(f"Jules response: {result}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    print("Jules #2 invoked successfully")

if __name__ == "__main__":
    main()
