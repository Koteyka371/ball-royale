import pytest
import sys
import copy
from unittest.mock import MagicMock
sys.path.insert(0, "src")

from ai.action import Action

class MockBall:
    def __init__(self, x=0, y=0, **kwargs):
        self.id = 1
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.radius = 10
        self.speed = 100
        self.hp = 100
        self.alive = True
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.get = lambda k, d=None: getattr(self, k, d)

class MockArena:
    def __init__(self):
        self.hazards = []

    def clamp_position(self, x, y, r):
        return x, y, False
    def update_zone(self, *args, **kwargs):
        pass

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.tick = 0
        self.balls = []
        self.width = 1000
        self.height = 1000

def test_geyser_boots():
    world = MockWorld()
    ball = MockBall(x=0, y=0)
    world.balls.append(ball)

    action = Action(ball, world)

    # 1. Collect booster
    class MockBooster:
        def __init__(self):
            self.kind = "geyser_boots"
            self.x = 0
            self.y = 0
            self.radius = 15
            self.active = True
        def get(self, k, d=None):
            return getattr(self, k, d)

    booster = MockBooster()
    world.boosters.append(booster)

    action.execute("collect_booster", 0.016)

    assert getattr(ball, "geyser_boots_timer", 0.0) > 0.0

    # 2. Interact with lava geyser
    class MockHazard:
        def __init__(self):
            self.kind = "lava_geyser"
            self.x = 0
            self.y = 0
            self.radius = 40
            self.active = True
            self.damage = 10
    geyser = MockHazard()

    world.arena.hazards.append(geyser)

    action.execute("chase", 0.016)

    assert getattr(ball, "is_in_lava", False) == False # Shouldn't be in lava
    assert getattr(ball, "fly_timer", 0.0) > 0.0 # Airborne
    assert getattr(ball, "speed_buff_timer", 0.0) > 0.0 # Speed boost
