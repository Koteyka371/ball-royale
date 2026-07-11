import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from ai.action import Action
import math

class MockBall:
    def __init__(self):
        self.x = 100.0
        self.y = 100.0
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.damage = 25.0
        self.attack_accuracy = 1.0

class MockWorld:
    pass

def test_projectile_recoil():
    world = MockWorld()
    attacker = MockBall()
    target = MockBall()
    target.x = 200.0
    target.y = 100.0

    action = Action(world, attacker)

    # Distance is 100. Melee range + buffer is 10 + 10 + 20 = 40. So it's ranged.
    # original_damage is 25.0, recoil force is 250.0.
    # target is at 200, attacker is at 100. dx = 100, dy = 0. nx = 1, ny = 0.
    # attacker.vx should be -250.0
    action._attempt_damage(attacker, target)

    assert attacker.vx == -250.0
    assert attacker.vy == 0.0

def test_melee_no_recoil():
    world = MockWorld()
    attacker = MockBall()
    target = MockBall()
    target.x = 110.0
    target.y = 100.0

    action = Action(world, attacker)

    # Distance is 10. Melee range is 40. Not ranged.
    action._attempt_damage(attacker, target)

    assert attacker.vx == 0.0
    assert attacker.vy == 0.0
