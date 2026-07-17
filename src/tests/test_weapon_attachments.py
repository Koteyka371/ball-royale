import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.action import Action

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.boosters = []
        self.balls = []

    def _deal_damage(self, attacker, target):
        target.take_damage(attacker.damage)

class MockBall:
    def __init__(self, id, x, y, team):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.radius = 10.0
        self.hp = 100.0
        self.damage = 10.0
        self.alive = True
        self.is_projectile = False
        self.is_energy = False
        self.intangible = False

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

def test_fire_attachment():
    world = MockWorld()
    b1 = MockBall(1, 100, 100, 1)
    b1.fire_attachment_timer = 15.0
    b2 = MockBall(2, 120, 100, 2)
    world.balls = [b1, b2]

    action = Action(b1, world)
    action._attempt_damage(b1, b2)

    assert getattr(b2, "dot_duration", 0.0) == 2.0
    assert getattr(b2, "dot_damage_per_tick", 0.0) == 2.0

def test_ice_attachment():
    world = MockWorld()
    b1 = MockBall(1, 100, 100, 1)
    b1.ice_attachment_timer = 15.0
    b2 = MockBall(2, 120, 100, 2)
    world.balls = [b1, b2]

    action = Action(b1, world)
    action._attempt_damage(b1, b2)

    assert getattr(b2, "slow_timer", 0.0) == 2.0

def test_spread_attachment():
    world = MockWorld()
    b1 = MockBall(1, 100, 100, 1)
    b1.spread_attachment_timer = 15.0
    b2 = MockBall(2, 120, 100, 2) # Target
    b3 = MockBall(3, 130, 100, 2) # Near target (dist 10)
    b4 = MockBall(4, 300, 300, 2) # Far from target
    world.balls = [b1, b2, b3, b4]

    action = Action(b1, world)
    action._attempt_damage(b1, b2)

    # b3 should take 50% damage
    assert b3.hp == 95.0
    # b4 shouldn't take damage
    assert b4.hp == 100.0

def test_pierce_attachment():
    world = MockWorld()
    b1 = MockBall(1, 100, 100, 1)
    b1.pierce_attachment_timer = 15.0
    b2 = MockBall(2, 120, 100, 2) # Target
    b3 = MockBall(3, 140, 100, 2) # Behind target (x axis aligns perfectly)
    b4 = MockBall(4, 100, 120, 2) # Beside attacker
    world.balls = [b1, b2, b3, b4]

    action = Action(b1, world)
    action._attempt_damage(b1, b2)

    # b3 should take 50% damage
    assert b3.hp == 95.0
    # b4 shouldn't take damage
    assert b4.hp == 100.0

def test_timer_decrement():
    world = MockWorld()
    b1 = MockBall(1, 100, 100, 1)
    b1.fire_attachment_timer = 15.0
    b1.ice_attachment_timer = 15.0
    b1.spread_attachment_timer = 15.0
    b1.pierce_attachment_timer = 15.0
    action = Action(b1, world)

    action.execute("idle", 1.0)

    assert b1.fire_attachment_timer == 14.0
    assert b1.ice_attachment_timer == 14.0
    assert b1.spread_attachment_timer == 14.0
    assert b1.pierce_attachment_timer == 14.0
