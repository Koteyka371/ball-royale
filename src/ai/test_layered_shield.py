import pytest
from ai.action import Action
import math

class MockBall:
    def __init__(self, id, x, y, team):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.damage = 10.0
        self.speed = 10.0
        self.reflect_shield_active = False
        self.reflect_shield_capacity = 0.0
        self.reflect_shield_layers = False
        self.reflect_shield_layer_size = 25.0

class MockWorld:
    def __init__(self):
        self.balls = []
        self.tick = 0
        self.leaderboard_manager = None

    def _deal_damage(self, attacker, target):
        pass

def test_layered_shield_absorbs_partially():
    world = MockWorld()
    attacker = MockBall(1, 0, 0, "A")
    attacker.damage = 40.0

    target = MockBall(2, 50, 0, "B")
    target.reflect_shield_active = True
    target.reflect_shield_capacity = 75.0
    target.reflect_shield_layers = True
    target.reflect_shield_layer_size = 25.0

    world.balls = [attacker, target]

    action = Action(target, world)
    action._attempt_damage(attacker, target)

    # Target had 75 capacity. Layer size is 25.
    # Current layer capacity = 75 % 25 = 0 -> 25.
    # It absorbs 25 damage out of 40 because of the layer size.
    assert target.reflect_shield_capacity == 50.0

def test_unlayered_shield():
    world = MockWorld()
    attacker = MockBall(1, 0, 0, "A")
    attacker.damage = 40.0

    target = MockBall(2, 50, 0, "B")
    target.reflect_shield_active = True
    target.reflect_shield_capacity = 75.0
    target.reflect_shield_layers = False

    world.balls = [attacker, target]

    action = Action(target, world)
    action._attempt_damage(attacker, target)

    # It absorbs all 40 damage.
    assert target.reflect_shield_capacity == 35.0

def test_unlayered_shield_breaks():
    world = MockWorld()
    attacker = MockBall(1, 0, 0, "A")
    attacker.damage = 80.0

    target = MockBall(2, 50, 0, "B")
    target.reflect_shield_active = True
    target.reflect_shield_capacity = 75.0
    target.reflect_shield_layers = False

    world.balls = [attacker, target]

    action = Action(target, world)
    action._attempt_damage(attacker, target)

    # Breaks the shield and capacity drops to 0.
    assert target.reflect_shield_active == False
    assert target.reflect_shield_capacity == 0.0

def test_layered_shield_multiple_hits():
    world = MockWorld()
    attacker = MockBall(1, 0, 0, "A")
    attacker.damage = 40.0

    target = MockBall(2, 50, 0, "B")
    target.reflect_shield_active = True
    target.reflect_shield_capacity = 60.0
    target.reflect_shield_layers = True
    target.reflect_shield_layer_size = 25.0

    world.balls = [attacker, target]

    action = Action(target, world)
    action._attempt_damage(attacker, target)

    # Cap is 60. Layer size 25. Current layer = 60 % 25 = 10.
    # It absorbs 10 damage out of 40.
    # Remainder 50.
    assert target.reflect_shield_capacity == 50.0

    action._attempt_damage(attacker, target)
    # Cap is 50. Layer size 25. Current layer = 50 % 25 = 0 -> 25.
    # Absorbs 25 damage out of 40.
    # Remainder 25.
    assert target.reflect_shield_capacity == 25.0
