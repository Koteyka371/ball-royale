import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_types_warrior import Warrior
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.dealt_damage = False

    def _deal_damage(self, attacker, target):
        self.dealt_damage = True

    def _collect_booster(self, ball, booster):
        pass

    def get_nearby_entities(self, ball, radius):
        return {
            "enemies": [],
            "allies": [],
            "boosters": [],
            "traps": []
        }

def test_level_up_mechanics():
    warrior = Warrior(1, 0, 0)
    warrior.radius = 20
    assert warrior.level == 1
    assert warrior.xp == 0.0

    warrior.level_up('hp')
    assert warrior.level == 2
    assert warrior.max_hp == 170

    warrior.level_up('damage')
    assert warrior.level == 3
    assert warrior.DAMAGE == 25

    warrior.level_up('speed')
    assert warrior.level == 4
    assert warrior.SPEED == 4.5

def test_damage_grants_xp():
    warrior1 = Warrior(1, 0, 0)
    warrior2 = Warrior(2, 0, 0)

    world = MockWorld()
    action = Action(warrior1, world)

    action._attempt_damage(warrior1, warrior2)

    assert warrior1.xp == 10.0

    # Do damage 9 more times to level up (100 xp needed)
    for _ in range(9):
        action._attempt_damage(warrior1, warrior2)

    assert warrior1.level == 2
    assert warrior1.xp == 0.0
    assert warrior1.xp_to_next_level == 150.0

def test_collect_booster_grants_xp():
    warrior = Warrior(1, 0, 0)
    warrior.radius = 20
    world = MockWorld()
    action = Action(warrior, world)

    class MockBooster:
        def __init__(self):
            self.x = 0
            self.y = 0
            self.radius = 10
            self.type = 'health'
            self.kind = 'powerup'

    # Give nearby booster
    world.get_nearby_entities = lambda b, r: {"enemies": [], "allies": [], "boosters": [MockBooster()], "traps": []}

    action.execute("collect_booster", 0.016)

    # _collect_booster logic path triggered
    assert warrior.xp >= 20.0
