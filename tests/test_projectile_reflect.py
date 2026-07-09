import pytest
from ai.action import Action
import math

class MockWorld:
    def __init__(self):
        self.events = []

class MockArena:
    def __init__(self):
        self.hazards = []

class MockBall:
    def __init__(self, x, y, radius=10):
        self.x = x
        self.y = y
        self.radius = radius
        self.hp = 100.0
        self.damage = 25.0
        self.ball_type = "basic"

def test_projectile_reflect_melee():
    world = MockWorld()
    world.arena = MockArena()
    attacker = MockBall(100, 100)
    target = MockBall(110, 100) # Close enough to be melee
    target.projectile_reflect_active = True

    action = Action(1, world)
    action.ball = target

    initial_target_hp = target.hp
    initial_attacker_hp = attacker.hp

    action._attempt_damage(attacker, target)

    # Since it's a melee attack, projectile reflect shouldn't block it.
    assert attacker.hp == initial_attacker_hp # no reflection

def test_projectile_reflect_ranged():
    world = MockWorld()
    world.arena = MockArena()
    attacker = MockBall(100, 100)
    target = MockBall(300, 100) # Far enough to be ranged
    target.projectile_reflect_active = True

    action = Action(1, world)
    action.ball = target

    initial_target_hp = target.hp
    initial_attacker_hp = attacker.hp

    action._attempt_damage(attacker, target)

    # It's a ranged attack, so attacker should take damage
    assert attacker.hp == initial_attacker_hp - attacker.damage

    # Also check that an event was added
    assert len(world.events) == 1
    assert world.events[0]['type'] == 'visual_effect'
    assert world.events[0]['data']['type'] == 'shield_block'
