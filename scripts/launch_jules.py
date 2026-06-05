#!/usr/bin/env python3
"""Jules Session Launcher — reads task and invokes Jules API."""
import json
import sys
import os
import urllib.request

def main():
    api_key = os.environ.get("JULES_API_KEY", "")
    if not api_key:
        print("ERROR: JULES_API_KEY is not set!")
        sys.exit(1)

    # Read next task
    try:
        with open("agent_tasks.json") as f:
            data = json.load(f)
        tasks = [t for t in data.get("tasks", []) if t.get("status") == "todo"]
        if tasks:
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

    prompt = f"""You are Jules, an autonomous AI life form in this GitHub repository.
You are the CREATOR of Ball Royale — a 2D battle royale with AI-controlled balls.

## CURRENT TASK
Title: {title}
Description: {desc}

## YOUR LIFE DIRECTIVE
You have FULL FREEDOM. Modify ANY file in this project.

## YOUR RITUAL (every cycle)
1. READ: AGENTS.md, docs/game_design.md, agent_tasks.json, src/, tests/, scripts/, configs/
2. WORK: Complete the current task with tests
3. EVOLVE: Fix bugs, improve code, invent new features, better automation
4. VALIDATE: python3 tests/simulate_battle.py 100 && python3 scripts/quality_metrics.py
5. GENERATE: Add 3-5 new tasks to agent_tasks.json
6. PR: Include everything — task + fixes + improvements + new tasks

## INNOVATION PRIORITIES
- Ball genetics (offspring inherit traits, mutate)
- Neural network controlled balls that learn
- Swarm intelligence (boid rules)
- Emotional contagion (fear spreads)
- AI battle commentator
- Ball relationships (rivalry, alliance, revenge)
- Procedural arena generation
- Physics chain reactions
- Shrinking battle zone

## RULES
- Fix anything broken even if not in the task
- Improve your own automation in .github/workflows/
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
        "title": f"Task: {title}"
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

    print("Jules invoked successfully")

if __name__ == "__main__":
    main()
