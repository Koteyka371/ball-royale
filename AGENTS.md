# Ball Royale — Working Guide for Jules/Codex

## CRITICAL RULE: All balls are AI-controlled

Every ball in the game is controlled by an in-built AI system. The player does NOT control balls directly. The player observes, or has limited interaction (speed, pause, camera focus).

## Source Priority

1. `agent_tasks.json` — machine-readable task queue
2. `docs/game_design.md` — game design document with AI system details
3. `docs/backlog.md` — human-readable backlog
4. `AGENTS.md` — this file

## What You Can Change

**You can modify ANY file in this project.** There are no restrictions. This includes:
- `src/` — game source code (Python and GDScript)
- `tests/` — test files
- `scripts/` — automation scripts
- `configs/` — configuration files
- `.github/workflows/` — CI/CD and automation
- `docs/` — documentation
- `agent_tasks.json` — task queue
- `AGENTS.md` — this file
- `CHANGELOG.md` — changelog

If you see something that needs improvement, improve it. Do not wait for permission.

## How to Work

### Step 1: READ the project
```bash
# Understand the full project
cat AGENTS.md
cat docs/game_design.md
cat agent_tasks.json
ls src/ tests/ scripts/ configs/
```

### Step 2: Pick and complete task
- Read `agent_tasks.json`, find first `todo` task
- Implement it with tests
- Make tests pass

### Step 3: Self-Improve (MANDATORY)
After the task, improve SOMETHING ELSE that helps the next run:
- Better scripts
- Better tests
- Better code
- Better docs
- Better CI/CD
- New tools
- Fix bugs you find
- Optimize slow code

### Step 4: Run validation
```bash
# Battle simulation (50-1000 balls)
python tests/simulate_battle.py 100

# Performance benchmark
python tests/benchmark_ai.py

# Code quality metrics
python scripts/quality_metrics.py

# Content generator (from JSON configs)
python scripts/generate_content.py

# All tests
pytest tests/ -v
```

### Step 5: Update agent_tasks.json
- Mark current task as `done`
- Add 3-5 new tasks (status: `todo`)

### Step 6: Create PR
- One task per PR
- Include all changes (current task + improvements + new tasks)

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

## Available Tools

| Tool | Purpose |
|------|---------|
| `tests/simulate_battle.py [N]` | Battle simulation with N balls (default 100) |
| `tests/benchmark_ai.py` | AI performance benchmark (60 FPS target) |
| `scripts/quality_metrics.py` | Code quality metrics |
| `scripts/generate_content.py` | Generate ball type code from JSON |
| `scripts/validate_tasks.py` | Validate agent_tasks.json |
| `scripts/analyze_project.py` | Project analysis |
| `scripts/generate_ideas.py` | Generate new ideas |

## Code Style

- Keep functions small and focused
- Write tests for new features
- Use meaningful variable names
- Comment complex AI logic

## Validation

```bash
# Before creating PR, run ALL of these:
python tests/simulate_battle.py 100
python tests/benchmark_ai.py
python scripts/quality_metrics.py
pytest tests/ -v
```
