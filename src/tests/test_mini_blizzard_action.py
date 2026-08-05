import pytest
from ai.action import Action
import math

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10.0
        self.speed_mult = 1.0
        self.freeze_stack = 0.0
        self.frozen_timer = 0.0
        self.hp = 100.0
        self._hp_tracker = []
        self.team = "blue"

    def take_damage(self, dmg, src=None):
        self.hp -= dmg
        self._hp_tracker.append((-dmg, src))

class MockHazard:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.radius = 30.0
        self.kind = kind
        self.damage = 10.0

class MockArena:
    def __init__(self):
        self.hazards = []

    def clamp_position(self, x, y, radius):
        return x, y, False

    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.projectiles = []
        self.balls = []

    def get_nearby_entities(self, obj, rad):
        return []

def test_mini_blizzard_effect():
    ball = MockBall(100.0, 100.0)
    world = MockWorld()
    world.balls.append(ball)

    # Within range
    hazard = MockHazard(110.0, 110.0, "mini_blizzard")
    world.arena.hazards.append(hazard)

    action = Action(ball, world)

    # 5 frames
    for _ in range(5):
        action.execute("idle", 1.0) # delta=1.0 for testing freeze stack quickly

    assert ball.speed_mult < 1.0
    assert ball.hp < 100.0
    assert ball.frozen_timer >= 2.0
