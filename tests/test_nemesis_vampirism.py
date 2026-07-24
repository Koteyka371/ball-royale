import pytest
import os
import sys

# Ensure src is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from system.profile import ProfileManager
from ai.action import Action
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id, type, hp=100.0, damage=10.0, x=0.0, y=0.0):
        self.id = id
        self.ball_type = type
        self.hp = hp
        self.max_hp = 100.0
        self.damage = damage
        self.kills = 0
        self.charge_level = 0.0
        self.x = x
        self.y = y
        self.radius = 10.0
        self.base_speed = 2.0
        self._base_speed_set = True
        self.team = "team" + str(id)

class MockGameMode:
    def __init__(self, name):
        self.name = name

class MockWorld:
    def __init__(self):
        self.balls = []
        self.profile_manager = None
        self.mode = None

    def _deal_damage(self, attacker, target):
        target.hp -= getattr(attacker, 'damage', 10.0)


def test_nemesis_vampirism_mode_healing():
    world = MockWorld()
    world.mode = MockGameMode("Nemesis Vampirism")

    attacker = MockBall(1, "type_A", hp=50) # Started at 50 hp
    target = MockBall(2, "type_B", hp=100) # Started at 100 hp
    world.balls = [attacker, target]

    pm = ProfileManager("test_nemesis_vampirism_profile.json")
    world.profile_manager = pm

    # Make Target the Nemesis of Attacker. Target kills Attacker twice.
    pm.add_kill(target.ball_type, attacker.ball_type)
    pm.add_kill(target.ball_type, attacker.ball_type)

    assert pm.is_nemesis(target.ball_type, attacker.ball_type) == True

    # Attacker does 10 damage to target.
    action = Action(attacker, world)
    action._attempt_damage(attacker, target)

    # Target should take 10 damage.
    # Attacker should heal for 100% of damage dealt (10 hp).
    assert target.hp <= 90.0  # it may take more depending on nemesis rules but shouldn't be 100
    damage_taken = 100.0 - target.hp
    assert damage_taken > 0

    assert attacker.hp == min(50.0 + damage_taken, 100.0)

    # Cleanup
    if os.path.exists("test_nemesis_vampirism_profile.json"):
        os.remove("test_nemesis_vampirism_profile.json")

def test_game_mode_registered():
    assert "nemesis_vampirism" in GAME_MODES
    assert GAME_MODES["nemesis_vampirism"].name == "Nemesis Vampirism"
