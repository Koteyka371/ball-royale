"""Generate new ideas from game_design.md and suggest tasks."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def load_game_design(path: Path) -> str:
    """Load game design document."""
    with path.open("r", encoding="utf-8") as f:
        return f.read()


def load_manifest(path: Path) -> dict[str, Any]:
    """Load task manifest."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def extract_ideas(design_text: str) -> list[dict[str, str]]:
    """Extract ideas from game design document."""
    ideas = []
    
    checkbox_pattern = r'- \[ \]\s*(.+)'
    for match in re.finditer(checkbox_pattern, design_text):
        ideas.append({
            "type": "feature",
            "title": match.group(1).strip(),
            "source": "game_design.md"
        })
    
    ball_pattern = r'###\s*(\w+)\s*\('
    for match in re.finditer(ball_pattern, design_text):
        ideas.append({
            "type": "ball_type",
            "title": f"Implement {match.group(1)} ball",
            "source": "game_design.md"
        })
    
    arena_pattern = r'\d+\.\s*\*\*(.+?)\*\*'
    for match in re.finditer(arena_pattern, design_text):
        ideas.append({
            "type": "arena",
            "title": f"Create {match.group(1)} arena",
            "source": "game_design.md"
        })
    
    return ideas


def find_new_ideas(
    ideas: list[dict[str, str]],
    manifest: dict[str, Any]
) -> list[dict[str, str]]:
    """Find ideas not yet in task list."""
    existing_titles = {t["title"].lower() for t in manifest.get("tasks", [])}
    new_ideas = []
    
    for idea in ideas:
        if idea["title"].lower() not in existing_titles:
            new_ideas.append(idea)
    
    return new_ideas


def generate_task_from_idea(idea: dict[str, str], index: int) -> dict[str, Any]:
    """Generate a task from an idea."""
    task_id = f"idea-{idea['type']}-{index:03d}"
    
    risk_map = {
        "feature": "medium",
        "ball_type": "medium",
        "arena": "low",
        "skill": "medium",
        "ai": "medium"
    }
    
    area_map = {
        "feature": "content",
        "ball_type": "content",
        "arena": "arenas",
        "skill": "skills",
        "ai": "ai-core"
    }
    
    paths_map = {
        "arena": [
            "src/arena/arena_types.py",
            "src/arena/arena_types.gd",
            "src/arena/procedural_arena.py",
            "src/arena/procedural_arena.gd",
            "tests/test_arena_*.py",
            "tests/test_procedural_*.py",
            "src/arena/test_*.py"
        ],
        "ball_type": [
            "src/ai/ball_types_*.py",
            "src/ai/action.py",
            "src/ai/action.gd"
        ],
        "ai": [
            "src/ai/ball_brain.py",
            "src/ai/decision.py",
            "src/ai/perception.py",
            "src/ai/emotion.py"
        ],
        "skill": [
            "src/ai/action.py",
            "src/ai/action.gd",
            "tests/test_action*.py"
        ]
    }
    
    return {
        "id": task_id,
        "status": "todo",
        "area": area_map.get(idea["type"], "content"),
        "risk": risk_map.get(idea["type"], "medium"),
        "title": idea["title"],
        "description": f"Implement {idea['title']} as described in game_design.md",
        "allowed_paths": paths_map.get(idea["type"], ["src/ai/**", "src/arena/**", "tests/**"]),
        "acceptance": [
            f"{idea['title']} implemented",
            "Tests pass",
            "No regressions"
        ]
    }


def main():
    """Main entry point."""
    design_path = Path("docs/game_design.md")
    manifest_path = Path("agent_tasks.json")
    
    if not design_path.exists():
        print("Error: docs/game_design.md not found")
        return 1
    
    if not manifest_path.exists():
        print("Error: agent_tasks.json not found")
        return 1
    
    design_text = load_game_design(design_path)
    manifest = load_manifest(manifest_path)
    
    print("=" * 60)
    print("BALL ROYALE - IDEA GENERATOR")
    print("=" * 60)
    
    ideas = extract_ideas(design_text)
    print(f"\n[*] Found {len(ideas)} ideas in game_design.md")
    
    new_ideas = find_new_ideas(ideas, manifest)
    print(f"[NEW] {len(new_ideas)} new ideas not in task list")
    
    if new_ideas:
        print("\n[NEW IDEAS]")
        for i, idea in enumerate(new_ideas[:10], 1):
            print(f"  {i}. [{idea['type']}] {idea['title']}")
        
        print("\n[GENERATING TASKS...]")
        tasks_to_add = []
        for i, idea in enumerate(new_ideas[:5], 1):
            task = generate_task_from_idea(idea, len(manifest.get("tasks", [])) + i)
            tasks_to_add.append(task)
            print(f"  + {task['id']}: {task['title']}")
        
        manifest["tasks"].extend(tasks_to_add)
        with manifest_path.open("w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        print(f"\n[OK] Added {len(tasks_to_add)} new tasks to agent_tasks.json")
    else:
        print("\n[OK] No new ideas - all features are in task list!")
    
    print("\n[SUGGESTED NEXT STEPS]")
    todo_tasks = [t for t in manifest.get("tasks", []) if t.get("status") == "todo"]
    if todo_tasks:
        print(f"  1. Start with: {todo_tasks[0]['title']}")
        if len(todo_tasks) > 1:
            print(f"  2. Then: {todo_tasks[1]['title']}")
        if len(todo_tasks) > 2:
            print(f"  3. Finally: {todo_tasks[2]['title']}")
    else:
        print("  1. All tasks completed! Generate more from game_design.md")
    
    print("\n" + "=" * 60)
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
