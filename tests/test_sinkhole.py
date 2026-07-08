import pytest
import math
from ai.action import Action

class MockBall:
    def __init__(self, x=0.0, y=0.0, hp=100.0, speed=100.0):
        self.x = x
        self.y = y
        self.hp = hp
        self.base_speed = speed
        self.speed = speed
        self.alive = True
        self.status_effects = []
        self.is_dashing = False
        self.id = 1
        self.killer = ""
        self.traits = []

class MockHazard:
    def __init__(self, x=0.0, y=0.0, radius=50.0, kind="sinkhole", damage=10.0, active=True):
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.damage = damage
        self.id = id(self)
        self.active = active

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.time = 0.0

def test_sinkhole_effects():
    world = MockWorld()
    ball = MockBall(x=50.0, y=50.0, hp=100.0)
    sinkhole = MockHazard(x=50.0, y=50.0, radius=30.0, kind="sinkhole", damage=10.0)
    world.arena.hazards.append(sinkhole)

    action = Action(ball, world)

    # We call the private method directly for isolated testing
    if hasattr(action, '_apply_hazards'):
        action._apply_hazards(1.0, "idle")

        # Should take damage
        assert ball.hp < 100.0

        # Speed should be reduced
        assert ball.speed == 10.0 # 100.0 * 0.1

def test_massive_sinkhole_effects():
    world = MockWorld()
    ball = MockBall(x=70.0, y=50.0, hp=100.0)
    sinkhole = MockHazard(x=50.0, y=50.0, radius=30.0, kind="massive_sinkhole", damage=10.0)
    world.arena.hazards.append(sinkhole)

    action = Action(ball, world)
    if hasattr(action, '_apply_hazards'):
        action._apply_hazards(1.0, "idle")

        # Should take more damage
        assert ball.hp < 100.0
        assert ball.hp == 80.0

        # Speed should be reduced more
        assert ball.speed == 5.0 # 100.0 * 0.05
