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
pip install -r requirements.txt
python scripts/validate_tasks.py agent_tasks.json
python scripts/test_ai_behaviors.py
```

## Jules Infinite Loop Setup

### Step 1: Get Jules API Key

1. Go to https://jules.google.com
2. Sign in with GitHub
3. Go to Settings → API Keys
4. Create new API key
5. Copy the key

### Step 2: Add API Key to GitHub

1. Go to https://github.com/Koteyka371/ball-royale/settings
2. Secrets and variables → Actions
3. New repository secret
4. Name: `JULES_API_KEY`
5. Value: your API key from step 1

### Step 3: Install Jules GitHub App

1. Go to https://jules.google.com
2. Click "Install on GitHub"
3. Select your repository

### Step 4: Enable Workflow

1. Go to https://github.com/Koteyka371/ball-royale/actions
2. Click "Jules Infinite Loop"
3. Click "Run workflow"

That's it! Jules will now:
1. Pick the first `todo` task from `agent_tasks.json`
2. Implement it with code + tests
3. Create a PR
4. When PR is merged → triggers next task
5. Generate new tasks when queue is low

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

## Automation

| Workflow | Trigger | Description |
|----------|---------|-------------|
| Jules Infinite Loop | PR merged / Manual | Jules picks and implements next task |
| Auto-Improve | Daily | Generate new tasks from game_design.md |
| Test | On push | Validate and test code |

## AI System

Each ball has a **BallBrain** with 4 layers:
1. **Perception** - scan for enemies, allies, boosters
2. **Emotion** - fear, rage, greed based on situation
3. **Decision** - choose best action
4. **Action** - execute behavior

## License

MIT
