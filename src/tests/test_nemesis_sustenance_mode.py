import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.action import Action
from ai.game_modes import NemesisSustenanceMode

class MockProfileManager:
    def __init__(self):
        self.nemesis_map = {}

    def is_nemesis(self, t1, t2):
        if t1 in self.nemesis_map and self.nemesis_map[t1] == t2:
            return True
        return False

    def add_kill(self, k, v):
        pass

class MockWorld:
    def __init__(self):
        self.events = []
        self.balls = []
        self.mode = NemesisSustenanceMode()
        self.profile_manager = MockProfileManager()
    def _deal_damage(self, attacker, target):
        target.hp -= getattr(attacker, "damage", 10.0)

class MockBall:
    def __init__(self, id, ball_type, hp, max_hp, damage=10):
        self.id = id
        self.ball_type = ball_type
        self.hp = hp
        self.max_hp = max_hp
        self.damage = damage
        self.x = 0
        self.y = 0
        self.alive = True
        self.team = "team_a"
        self.inventory = []
        self.status_effects = []
        self.traits = []

def test_nemesis_sustenance_healing():
    world = MockWorld()

    # Set up nemesis relation: attacker's nemesis is target
    world.profile_manager.nemesis_map["attacker_ball"] = "target_ball"

    attacker = MockBall(1, "attacker_ball", hp=50, max_hp=100, damage=20)
    target = MockBall(2, "target_ball", hp=100, max_hp=100, damage=10)

    world.balls = [attacker, target]
    action = Action(attacker, world)

    # In action.py damage logic, if target is nemesis, damage is increased by 1.2
    # So 20 * 1.2 = 24 damage dealt.
    # Healing should be damage_dealt * 1.5 = 24 * 1.5 = 36
    # Expected attacker HP = 50 + 36 = 86

    action._attempt_damage_internal(attacker, target)

    # We expect the target to have taken damage
    # Depending on exactly what other damage modifiers apply, old_hp was 100, new_hp is ~76.
    assert target.hp < 100

    # Attacker should have been healed
    assert attacker.hp > 50
    assert attacker.hp == 80.0

def test_nemesis_sustenance_no_healing_non_nemesis():
    world = MockWorld()

    # Different relation
    world.profile_manager.nemesis_map["attacker_ball"] = "other_ball"

    attacker = MockBall(1, "attacker_ball", hp=50, max_hp=100, damage=20)
    target = MockBall(2, "target_ball", hp=100, max_hp=100, damage=10)

    world.balls = [attacker, target]
    action = Action(attacker, world)

    action._attempt_damage_internal(attacker, target)

    # Target takes damage
    assert target.hp < 100
    # No healing should occur because target is not nemesis
    assert attacker.hp == 50
