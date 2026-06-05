"""
Ball Royale — Content Generator
Generates Python/GDScript code from JSON ball type configs.
Run: python scripts/generate_content.py
"""

import json
import os
import sys
from pathlib import Path

CONFIGS_DIR = Path(__file__).parent.parent / "configs"
SRC_AI_DIR = Path(__file__).parent.parent / "src" / "ai"
TESTS_DIR = Path(__file__).parent.parent / "tests"


def load_ball_types() -> dict:
    config_path = CONFIGS_DIR / "ball_types.json"
    if not config_path.exists():
        print(f"ERROR: {config_path} not found")
        sys.exit(1)
    with open(config_path) as f:
        return json.load(f)


def generate_ball_class(name: str, cfg: dict) -> str:
    class_name = name.capitalize()
    return f'''"""
Auto-generated ball type: {class_name}
{cfg.get("description", "")}
"""

from typing import Any


class {class_name}:
    BALL_TYPE = "{name}"
    HP = {cfg["hp"]}
    SPEED = {cfg["speed"]}
    DAMAGE = {cfg["damage"]}
    RADIUS = {cfg["radius"]}
    PERCEPTION_RADIUS = {cfg["perception_radius"]}
    AGGRESSION = {cfg["aggression"]}
    COLOR = "{cfg["color"]}"
    SKILL = "{cfg["skill"]}"
    SKILL_COOLDOWN = {cfg["skill_cooldown"]}

    def __init__(self, ball_id: int, x: float = 0.0, y: float = 0.0):
        self.id = ball_id
        self.hp = self.HP
        self.max_hp = self.HP
        self.x = x
        self.y = y
        self.alive = True
        self.kills = 0
        self.current_action = "idle"
        self.skill_timer = 0.0
        self.personality = "{name}"

    def get_hp_percent(self) -> float:
        return self.hp / self.max_hp if self.max_hp > 0 else 0.0

    def flee(self, delta: float) -> None:
        self.current_action = "flee"

    def attack(self, delta: float) -> None:
        self.current_action = "attack"

    def defend(self, delta: float) -> None:
        self.current_action = "defend"

    def collect_booster(self, delta: float) -> None:
        self.current_action = "opportunistic"

    def idle(self, delta: float) -> None:
        self.current_action = "idle"

    def take_damage(self, amount: float) -> None:
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

    def use_skill(self) -> bool:
        if self.skill_timer <= 0:
            self.skill_timer = self.SKILL_COOLDOWN
            return True
        return False

    def __repr__(self) -> str:
        return f"{{self.BALL_TYPE}}#{{self.id}} HP={{self.hp}}/{{self.max_hp}} [{{self.current_action}}]"
'''


def generate_ball_tests(name: str, cfg: dict) -> str:
    class_name = name.capitalize()
    return f'''"""
Auto-generated tests for: {class_name}
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_types_{name} import {class_name}


def test_{name}_initialization():
    ball = {class_name}(ball_id=1, x=100, y=200)
    assert ball.id == 1
    assert ball.hp == {cfg["hp"]}
    assert ball.max_hp == {cfg["hp"]}
    assert ball.alive is True
    assert ball.personality == "{name}"


def test_{name}_hp_percent():
    ball = {class_name}(ball_id=1)
    ball.hp = {cfg["hp"] // 2}
    assert ball.get_hp_percent() == 0.5


def test_{name}_take_damage():
    ball = {class_name}(ball_id=1)
    ball.take_damage(50)
    assert ball.hp == {cfg["hp"] - 50}
    assert ball.alive is True
    ball.take_damage({cfg["hp"]})
    assert ball.alive is False


def test_{name}_skill():
    ball = {class_name}(ball_id=1)
    assert ball.use_skill() is True
    assert ball.skill_timer == {cfg["skill_cooldown"]}
    assert ball.use_skill() is False


def test_{name}_actions():
    ball = {class_name}(ball_id=1)
    ball.flee(0.016)
    assert ball.current_action == "flee"
    ball.attack(0.016)
    assert ball.current_action == "attack"
    ball.defend(0.016)
    assert ball.current_action == "defend"
    ball.collect_booster(0.016)
    assert ball.current_action == "opportunistic"
    ball.idle(0.016)
    assert ball.current_action == "idle"
'''


def generate_all():
    data = load_ball_types()
    ball_types = data.get("ball_types", {})

    print(f"Generating code for {len(ball_types)} ball types...")

    SRC_AI_DIR.mkdir(parents=True, exist_ok=True)
    TESTS_DIR.mkdir(parents=True, exist_ok=True)

    generated_files = []

    for name, cfg in ball_types.items():
        py_content = generate_ball_class(name, cfg)
        py_path = SRC_AI_DIR / f"ball_types_{name}.py"
        py_path.write_text(py_content, encoding="utf-8")
        generated_files.append(str(py_path))
        print(f"  Generated: {py_path}")

        test_content = generate_ball_tests(name, cfg)
        test_path = TESTS_DIR / f"test_ball_type_{name}.py"
        test_path.write_text(test_content, encoding="utf-8")
        generated_files.append(str(test_path))
        print(f"  Generated: {test_path}")

    print(f"\nGenerated {len(generated_files)} files")
    return generated_files


if __name__ == "__main__":
    generate_all()
