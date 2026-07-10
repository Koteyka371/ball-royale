import pytest
from ai.action import Action
import math

class MockWorld:
    def __init__(self):
        self.events = []
        self.balls = []
        self.profile_manager = None

    def get_events(self):
        return self.events

class MockArena:
    def __init__(self):
        self.hazards = []

class MockBall:
    def __init__(self, id, x, y, radius=10):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.hp = 100.0
        self.damage = 25.0
        self.ball_type = "basic"
        self.alive = True
    def take_damage(self, amount):
        self.hp -= amount

def test_projectile_reflect_melee():
    world = MockWorld()
    world.arena = MockArena()
    attacker = MockBall(1, 100, 100)
    target = MockBall(2, 110, 100) # Close enough to be melee
    target.projectile_reflect_active = True
    world.balls = [attacker, target]

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
    attacker = MockBall(1, 100, 100)
    target = MockBall(2, 300, 100) # Far enough to be ranged
    target.projectile_reflect_active = True
    world.balls = [attacker, target]

    action = Action(1, world)
    action.ball = target

    initial_target_hp = target.hp
    initial_attacker_hp = attacker.hp

    action._attempt_damage(attacker, target)

    # It's a ranged attack, so target should deflect it and create a suspended projectile
    assert attacker.hp == initial_attacker_hp

    assert hasattr(target, "suspended_projectiles")
    assert len(target.suspended_projectiles) == 1
    proj = target.suspended_projectiles[0]
    assert proj["target"] == attacker
    assert proj["damage"] == attacker.damage
    assert proj["type"] == "reflected_projectile"

    # Also check that an event was added
    assert len(world.events) == 1
    assert world.events[0]['type'] == 'visual_effect'
    assert world.events[0]['data']['type'] == 'shield_block'

def test_projectile_reflect_timer_expiration():
    world = MockWorld()
    world.arena = MockArena()
    target = MockBall(1, 100, 100)
    target.projectile_reflect_active = True
    target.projectile_reflect_timer = 2.0
    world.balls = [target]

    action = Action(target, world)

    # Execute action to reduce timer
    action.execute("wander", 2.0)

    # Assert timer expired and active is False
    assert target.projectile_reflect_timer <= 0
    assert target.projectile_reflect_active == False
