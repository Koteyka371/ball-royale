# Ball Royale

2D арена-батл-рояль с самуправляемыми шариками. Все шарики управляются встроенным ИИ.

## Features

- 6+ игровых режимов
- 10+ типов шариков с уникальным ИИ
- 10+ арен
- 20+ скиллов
- Автономное ИИ-управление каждым шариком

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Validate tasks
python scripts/validate_tasks.py agent_tasks.json

# Run tests
python scripts/test_ai_behaviors.py

# Analyze project
python scripts/analyze_project.py

# Generate ideas
python scripts/generate_ideas.py
```

## Project Structure

```
ball-royale/
├── agent_tasks.json          # Task queue
├── AGENTS.md                 # Instructions for AI
├── docs/
│   ├── game_design.md        # Game design document
│   └── backlog.md            # Backlog
├── scripts/                  # Automation tools
├── src/                      # Game source code
├── tests/                    # Tests
└── .github/workflows/        # CI/CD
```

## Automation (GitHub Actions)

### Auto-Improve (Daily)
- Runs every day at 10:00 UTC
- Analyzes project state
- Generates new tasks from `game_design.md`
- Creates PR with updates

### Test (On Push)
- Runs on every push to main
- Validates task manifest
- Runs AI behavior tests
- Checks project status

### Issue to Task
- Add label `task` to any issue
- Issue is automatically converted to task in `agent_tasks.json`

## How It Works

1. **Tasks** are defined in `agent_tasks.json`
2. **Game design** is in `docs/game_design.md`
3. **Scripts** analyze and generate new tasks
4. **GitHub Actions** runs automatically
5. **PRs** are created with improvements

## AI System

Each ball has a **BallBrain** with 4 layers:
1. **Perception** - scan for enemies, allies, boosters
2. **Emotion** - fear, rage, greed based on situation
3. **Decision** - choose best action
4. **Action** - execute behavior

## Contributing

1. Create an issue with label `task`
2. Issue is converted to task automatically
3. Implement the task
4. Create PR
5. CI runs tests
6. Merge when ready

## License

MIT
