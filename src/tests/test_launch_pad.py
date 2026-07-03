import pytest
from ai.action import Action
from arena.procedural_arena import Hazard
import math

class MockBall:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.hp = 100.0
        self.speed = 2.0
        self.team = "A"

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000
        self.is_foggy = False
        self.safe_zone_center = (500, 500)
        self.safe_zone_radius = 5000

    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.boosters = []
        self.tick = 0

def test_launch_pad_logic():
    ball = MockBall(100.0, 100.0)
    world = MockWorld()
    world.balls.append(ball)

    pad = Hazard(1, 100.0, 100.0, 30.0, "launch_pad", 0.0)
    pad.target_x = 500.0
    pad.target_y = 500.0
    world.arena.hazards.append(pad)

    action = Action(ball, world)
    action.execute("idle", 0.016)

    assert getattr(ball, "is_flying", False) == True
    assert getattr(ball, "fly_timer", 0.0) > 0.0
    assert getattr(ball, "fly_target_x", None) == 500.0
    assert getattr(ball, "fly_target_y", None) == 500.0

def test_flying_logic():
    ball = MockBall(100.0, 100.0)
    world = MockWorld()
    world.balls.append(ball)

    ball.is_flying = True
    ball.fly_timer = 1.0
    ball.fly_target_x = 500.0
    ball.fly_target_y = 500.0
    ball.zone_immunity_timer = 1.0

    action = Action(ball, world)
    action.execute("idle", 0.016)

    # Check that ball moved towards target
    assert ball.x > 100.0
    assert ball.y > 100.0

    # Check that it's immune to something (zone_immunity_timer should still be > 0)
    assert getattr(ball, "zone_immunity_timer", 0.0) > 0.0
