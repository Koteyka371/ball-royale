import pytest
import math
from src.ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
        self.is_eclipse = False
        self.is_raining = False
        self.is_foggy = False
        self.is_night = False
    def clamp_position(self, x, y, r):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []
        self.width = 1000
        self.height = 1000

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 0
        self.y = 0
        self.radius = 10
        self.alive = True
        self.speed = 100
        self.base_speed = 100
        self.damage = 10
        self.base_damage = 10
        self.stamina = 100
        self.max_stamina = 100
        self.hp = 100
        self.max_hp = 100

class Hazard:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.radius = 5.0
        self.damage = 10.0
        self.duration = 5.0

def test_shrapnel_merge():
    world = MockWorld()
    ball = MockBall()
    world.balls.append(ball)
    action = Action(ball, world)

    # Place two shrapnels that overlap
    h1 = Hazard("shrapnel", 10, 10)
    h2 = Hazard("shrapnel", 12, 12)
    world.arena.hazards = [h1, h2]

    action.execute("idle", 0.1)

    # One of them should be merged
    assert getattr(h2, "_merged", False) or getattr(h1, "_merged", False)

    # Find the active one
    active = [h for h in world.arena.hazards if getattr(h, "duration", 0) > 0 and not getattr(h, "_merged", False)]
    assert len(active) == 1

    merged_hazard = active[0]

    # Should have increased radius, damage, and duration
    assert merged_hazard.radius > 5.0
    assert merged_hazard.damage > 10.0
    assert merged_hazard.duration > 5.0
