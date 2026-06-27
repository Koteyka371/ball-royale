"""Generate new tasks from game_design.md and current project state."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


TASK_TEMPLATE = {
    "status": "todo",
    "area": "content",
    "risk": "medium",
    "allowed_paths": ["src/**", "tests/**"],
    "acceptance": ["Feature works", "Tests pass"]
}


def load_manifest(path: Path) -> dict[str, Any]:
    """Load task manifest."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_game_design(path: Path) -> str:
    """Load game design document."""
    with path.open("r", encoding="utf-8") as f:
        return f.read()


def extract_features(design_text: str) -> list[dict[str, str]]:
    """Extract feature ideas from game design document."""
    features = []
    
    # Find ball types
    ball_pattern = r'\|\s*(\w+)\s*\|.*?\|.*?\|.*?\|'
    for match in re.finditer(ball_pattern, design_text):
        name = match.group(1)
        if name not in ("Имя", "---"):
            features.append({
                "title": f"Implement {name} ball",
                "description": f"Create {name} ball type with unique stats and skill",
                "area": "content"
            })
    
    # Find arenas
    arena_pattern = r'\d+\.\s*\*\*(.+?)\*\*'
    for match in re.finditer(arena_pattern, design_text):
        name = match.group(1)
        if "Arena" in name or "Pit" in name or "Island" in name:
            features.append({
                "title": f"Create {name} arena",
                "description": f"Implement {name} with unique mechanics",
                "area": "arenas"
            })
    
    # Find skills
    skill_pattern = r'\d+\.\s*(.+?)\s*\((.+?)\)'
    for match in re.finditer(skill_pattern, design_text):
        name = match.group(1)
        desc = match.group(2)
        features.append({
            "title": f"Implement {name} skill",
            "description": f"Create {name} skill: {desc}",
            "area": "skills"
        })
    
    # Find game modes
    mode_pattern = r'###\s*(.+?)\s*\n'
    for match in re.finditer(mode_pattern, design_text):
        name = match.group(1)
        if "Mode" in name or "Battle" in name or "Racing" in name:
            features.append({
                "title": f"Implement {name} game mode",
                "description": f"Create {name} with full rules and mechanics",
                "area": "modes"
            })
    
    return features


def find_missing_tasks(manifest: dict[str, Any], features: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Find features not yet in task list."""
    existing_titles = {t["title"].lower() for t in manifest.get("tasks", [])}
    new_tasks = []
    
    paths_map = {
        "arenas": [
            "src/arena/arena_types.py",
            "src/arena/arena_types.gd",
            "src/arena/procedural_arena.py",
            "src/arena/procedural_arena.gd",
            "tests/test_arena_*.py",
            "tests/test_procedural_*.py",
            "src/arena/test_*.py"
        ],
        "content": [
            "src/ai/ball_types_*.py",
            "src/ai/action.py",
            "src/ai/action.gd"
        ],
        "skills": [
            "src/ai/action.py",
            "src/ai/action.gd",
            "tests/test_action*.py"
        ],
        "modes": [
            "src/ai/game_modes.py",
            "src/ai/game_modes.gd",
            "tests/test_game_modes.py"
        ]
    }
    
    for feature in features:
        if feature["title"].lower() not in existing_titles:
            task = {
                "id": f"auto-{feature['title'].lower().replace(' ', '-')[:50]}",
                **TASK_TEMPLATE,
                "allowed_paths": paths_map.get(feature["area"], ["src/ai/**", "src/arena/**", "tests/**"]),
                **feature
            }
            new_tasks.append(task)
    
    return new_tasks


def main():
    """Main entry point."""
    manifest_path = Path("agent_tasks.json")
    design_path = Path("docs/game_design.md")
    
    if not manifest_path.exists():
        print("Error: agent_tasks.json not found")
        return 1
    
    if not design_path.exists():
        print("Error: docs/game_design.md not found")
        return 1
    
    manifest = load_manifest(manifest_path)
    design_text = load_game_design(design_path)
    
    # Extract features from design doc
    features = extract_features(design_text)
    print(f"Found {len(features)} features in game_design.md")
    
    # Find what's missing
    new_tasks = find_missing_tasks(manifest, features)
    print(f"Generated {len(new_tasks)} new tasks")
    
    # Add to manifest
    if new_tasks:
        manifest["tasks"].extend(new_tasks)
        
        # Save updated manifest
        with manifest_path.open("w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        print(f"Added {len(new_tasks)} tasks to agent_tasks.json")
        
        # Show new tasks
        for task in new_tasks[:5]:
            print(f"  - {task['id']}: {task['title']}")
    else:
        print("No new tasks to add")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
