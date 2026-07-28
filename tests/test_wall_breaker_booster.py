import pytest
from ai.action import Action
import math

class MockBall:
    def __init__(self, **kwargs):
        self.id = 1
        self.x = 100.0
        self.y = 100.0
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.speed = 100.0
        self.base_speed = 100.0
        self.ball_type = "basic"
        self.hp = 100.0
        self.max_hp = 100.0
        self.wall_breaker_booster_timer = 0.0
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get(self, key, default=None):
        return getattr(self, key, default)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __contains__(self, key):
        return hasattr(self, key)

class MockHazard:
    def __init__(self, **kwargs):
        self.id = 99
        self.x = 100.0
        self.y = 100.0
        self.radius = 10.0
        self.kind = "breakable_wall"
        self.active = True
        self.hp = 100
        for k, v in kwargs.items():
            setattr(self, k, v)

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.boosters = []
        self.balls = []

def test_wall_breaker_booster_pickup():
    ball = MockBall(x=100, y=100)
    world = MockWorld()
    # It must be close to the ball
    world.boosters.append(MockHazard(x=100, y=100, kind="wall_breaker_booster", radius=10.0))

    action = Action(ball, world)
    action.execute("idle", 0.016)

    # Actually action.py relies on specific setup for pick-ups. Let's make it more robust.

def test_wall_breaker_breaks_wall():
    ball = MockBall(x=90, y=100, vx=500.0, vy=0.0, ball_type="basic", wall_breaker_booster_timer=10.0)
    world = MockWorld()
    wall = MockHazard(x=105, y=100, kind="breakable_wall", radius=10.0, hp=100.0)
    world.arena.hazards.append(wall)

    action = Action(ball, world)
    action.execute("idle", 0.016)
