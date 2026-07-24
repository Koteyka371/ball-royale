import pytest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.events = []
        self.arena = self
        self.hazards = []

class MockTarget:
    def __init__(self):
        self.kinetic_shield_active = True
        self.kinetic_shield_stored_damage = 25.0
        self.x = 0
        self.y = 0
        self.id = 1
        self.radius = 10
        self.speed_boost_timer = 3.0
        self.speed = 100.0
        self.base_speed = 100.0
        self.courage_timer = 0.0

def test_kinetic_shield():
    world = MockWorld()
    target = MockTarget()
    action = Action(target, world)

    action.execute("dummy", 0.1)

    assert target.speed_boost_timer == 2.9
    assert target.speed == 100.0 * (1.0 + min(25.0 / 50.0, 3.0))
