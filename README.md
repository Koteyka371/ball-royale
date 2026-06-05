# Ball Royale

2D арена-батл-рояль с самуправляемыми шариками. Идеально для коротких YouTube/Shorts видео.

## Features

- 6+ игровых режимов (Battle Royale, Team Battle, Racing, Survival, Sumo, King of the Hill)
- 10+ типов шариков (Warrior, Scout, Tank, Healer, Sniper, Bomber, etc.)
- 10+ арен (Classic, Death Valley, Sky Island, Lava Pit, etc.)
- 20+ скиллов (wave attack, dash, shield, heal, snipe, bomb, etc.)
- Автоматическое управление шариками + вмешательство игрока
- Эпичные эффекты: частицы, взрывы, следы
- Идеально для YouTube Shorts (30-60 секунд)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Validate task manifest
python scripts/validate_tasks.py agent_tasks.json

# Generate new tasks from game_design.md
python scripts/generate_tasks.py

# Run tests
pytest tests/ -v
```

## Project Structure

```
ball-royale/
├── agent_tasks.json          # Task queue (56 tasks)
├── AGENTS.md                 # Instructions for AI agents
├── docs/
│   ├── game_design.md        # Full game design document
│   └── backlog.md            # Detailed backlog
├── scripts/
│   ├── validate_tasks.py     # Task manifest validator
│   └── generate_tasks.py     # Auto-generate tasks from design
├── src/                      # Game source code (TBD)
├── tests/                    # Tests (TBD)
└── .github/workflows/        # CI/CD
```

## Self-Improvement Loop

This project uses an automated self-improvement loop:

1. `agent_tasks.json` contains 56+ tasks
2. Jules/Codex picks the first `todo` task
3. Implements it with code + tests
4. Creates a PR
5. CI validates and tests
6. Auto-merges if safe (low/medium risk)
7. `generate_tasks.py` creates new tasks from `game_design.md`

## Game Modes

### 1. Battle Royale (Main)
- 20-50 balls on arena
- Arena shrinks every 5 seconds
- Last ball standing wins

### 2. Team Battle
- 4 teams (Red, Blue, Green, Yellow)
- Each team has unique bonus
- Destroy enemy flags to win

### 3. Racing
- Balls race on track with obstacles
- First to finish wins

### 4. Survival
- 1 ball vs 50 enemies
- Waves get harder
- Survive as long as possible

### 5. Sumo
- Push opponents off platform
- Last one standing wins

### 6. King of the Hill
- Control the throne
- Most points wins

## Ball Types

| Ball | Color | Skill | Role |
|------|-------|-------|------|
| Warrior | 🔴 Red | Wave Attack | Damage |
| Scout | 🔵 Blue | Dash | Speed |
| Tank | 🟢 Green | Shield | Defense |
| Healer | 🟡 Yellow | Heal | Support |
| Sniper | 🟣 Purple | Snipe | Ranged |
| Bomber | 🟠 Orange | Bomb | AoE |
| Ninja | ⚫ Black | Stealth | Assassin |
| King | 👑 Gold | Buff | Leader |

## YouTube Strategy

- **Duration**: 30-60 seconds (perfect for Shorts)
- **Format**: Vertical (9:16)
- **Content**: Epic moments, clutch plays, funny chaos
- **Viral elements**: Comebacks, 1v1 finals, unexpected plays

## Development

See `AGENTS.md` for detailed instructions on how Jules/Codex should work with this project.

## License

TBD
