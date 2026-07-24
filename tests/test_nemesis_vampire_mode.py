import pytest
import sys
sys.path.insert(0, "src")
from ai.game_modes import GAME_MODES

class MockProfileManager:
    def is_nemesis(self, attacker, target):
        return attacker == "vampire" and target == "nemesis"

class MockBall:
    def __init__(self, ball_type, hp, max_hp):
        self.ball_type = ball_type
        self.hp = hp
        self.max_hp = max_hp

class MockWorld:
    def __init__(self):
        self.profile_manager = MockProfileManager()

def test_nemesis_vampire_mode():
    mode = GAME_MODES.get("nemesis_vampire")
    assert mode is not None

    world = MockWorld()
    attacker = MockBall("vampire", 50.0, 100.0)
    target = MockBall("nemesis", 100.0, 100.0)

    # Should heal for 100% of damage
    mode.on_damage_dealt(world, attacker, target, 20.0)
    assert attacker.hp == 70.0

    # Non-nemesis shouldn't heal
    other = MockBall("other", 100.0, 100.0)
    mode.on_damage_dealt(world, attacker, other, 20.0)
    assert attacker.hp == 70.0

    # Don't heal past max hp
    mode.on_damage_dealt(world, attacker, target, 50.0)
    assert attacker.hp == 100.0
