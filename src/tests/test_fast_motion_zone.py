
import math
import sys
import pytest

sys.path.append("src")
from ai.action import Action

class DummyWorld:
    def __init__(self):
        self.arena = DummyArena()

class DummyArena:
    def __init__(self):
        self.hazards = []

class DummyHazard:
    def __init__(self, x, y, r, kind):
        self.x = x
        self.y = y
        self.radius = r
        self.kind = kind

class DummyBall:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.radius = 10
        self.hp = 100
        self.alive = True
        self.damage = 10
        self.ball_type = "sniper"
        self.base_speed = 100.0
        self.speed = 100.0
        self.speed_multiplier = 1.0
        self.skill_timer = 5.0
        self.max_stamina = 100.0
        self.stamina = 100.0
        self.is_exhausted = False

def test_fast_motion_zone():
    world = DummyWorld()
    ball = DummyBall()

    action = Action(1, world)
    action.ball = ball

    world.arena.hazards.append(DummyHazard(0, 0, 50.0, "fast_motion_zone"))

    action.execute("idle", 1.0)

    assert getattr(ball, "fast_motion_zone_active", False) == True
    assert ball.speed == 150.0
    assert ball.speed_multiplier == 1.5

    assert math.isclose(ball.skill_timer, 3.5)

    # Check stamina drain (100.0 - 60.0 * 1.0) = 40.0
    assert math.isclose(ball.stamina, 40.0)
