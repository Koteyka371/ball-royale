import pytest
from system.profile import ProfileManager
from ai.action import Action
from ai.game_modes import GAME_MODES
import os

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

class MockWorld:
    def __init__(self):
        self.balls = []
        self.profile_manager = None
        self.game_mode = None
        self.events = []

    def _deal_damage(self, attacker, target):
        target.hp -= attacker.damage

def test_nemesis_vampire_mode_healing():
    world = MockWorld()
    world.game_mode = GAME_MODES["nemesis_vampire"]

    # Create an attacker and target
    attacker = MockBall(1, "nemesis_attacker", hp=50) # HP is 50, not full
    target = MockBall(2, "nemesis_victim", hp=100)
    world.balls = [attacker, target]

    pm = ProfileManager("test_nemesis_vampire_profile.json")
    world.profile_manager = pm

    # Simulate killing the same victim twice to trigger nemesis
    pm.add_kill(attacker.ball_type, target.ball_type)
    pm.add_kill(attacker.ball_type, target.ball_type)

    assert pm.is_nemesis(attacker.ball_type, target.ball_type) == True

    action = Action(attacker, world)

    # In standard, Nemesis deals +20% damage (10 * 1.2 = 12.0)
    # In Nemesis Vampire mode, damage is converted to healing for the attacker.
    # Attacker HP goes from 50 to 50 + 12 = 62.
    # Target HP remains 100.

    action._attempt_damage(attacker, target)

    assert target.hp == 100.0
    assert abs(attacker.hp - 60.0) < 0.01

    if os.path.exists("test_nemesis_vampire_profile.json"):
        os.remove("test_nemesis_vampire_profile.json")
