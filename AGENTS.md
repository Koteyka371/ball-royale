# Ball Royale — Working Guide for Jules/Codex

## CRITICAL RULE: All balls are AI-controlled

Every ball in the game is controlled by an in-built AI system. The player does NOT control balls directly. The player observes, or has limited interaction (speed, pause, camera focus).

## Source Priority

1. `agent_tasks.json` — machine-readable task queue
2. `docs/game_design.md` — game design document with AI system details
3. `docs/backlog.md` — human-readable backlog
4. `AGENTS.md` — this file

## How to Work

### Step 1: Analyze Project State
```bash
# Check project status
python scripts/analyze_project.py

# Check test results
python scripts/auto_test.py

# Generate new ideas
python scripts/generate_ideas.py
```

### Step 2: Pick Task
```bash
# Validate manifest
python scripts/validate_tasks.py agent_tasks.json

# See next task
# Read agent_tasks.json and find first "todo" task
```

### Step 3: Implement
1. Create code in `src/`
2. Create tests in `tests/`
3. Run tests: `pytest tests/ -v`

### Step 4: Verify
```bash
# Run all checks
python scripts/auto_test.py

# Analyze progress
python scripts/analyze_project.py
```

### Step 5: Update Manifest
- Change task status to "done"
- If fewer than 5 todo tasks, run: `python scripts/generate_ideas.py`

### Step 6: Commit
```bash
git add .
git commit -m "feat: [task-title]"
git push
```

## AI System Architecture

Each ball has a BallBrain with 4 layers:
1. **Perception**: Scan for enemies, allies, boosters
2. **Emotion**: Fear, rage, greed based on situation
3. **Decision**: Choose best action
4. **Execute**: Move, attack, use skill, flee

## Task Selection Rules

- Always pick the first `todo` task
- Prioritize AI-related tasks
- Each PR = one task ID
- Do not expand PR scope

## Risk Rules

Do NOT auto-merge:
- Changes to CI/CD
- New external dependencies
- Security-sensitive code
- High/critical risk tasks

## Code Style

- Keep functions small and focused
- Write tests for new features
- Use meaningful variable names
- Comment complex AI logic

## Self-Improvement

After each task:
1. Run `python scripts/analyze_project.py`
2. Run `python scripts/generate_ideas.py`
3. Check if new tasks were generated
4. Continue with next task

## Validation

```bash
# Validate task manifest
python scripts/validate_tasks.py agent_tasks.json

# Run all tests
python scripts/auto_test.py

# Analyze project
python scripts/analyze_project.py

# Generate ideas
python scripts/generate_ideas.py

# Run pytest
pytest tests/ -v
```
