import pytest
import math
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
        self.danger_grid = {}
        self.width = 1000
        self.height = 1000
        self.safe_zone_radius = 500
        self.safe_zone_center = (500, 500)

    def clamp_position(self, x, y, r):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.entities = []
        self.boosters = []
        self.events = []
        self.time = 0.0
    def get_nearby_entities(self, ball, radius):
        return {"boosters": self.boosters, "balls": self.balls, "entities": self.entities}

class MockHazard:
    def __init__(self, hid, x, y, kind="hazard", radius=10):
        self.id = hid
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = radius
        self.frozen_timer = 0.0
        self.active = True
    def __init__(self, hid, x, y, kind="hazard", radius=10):
        self.id = hid
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = radius
        self.frozen_timer = 0.0

class MockBall:
    def __init__(self, bid, x, y, radius=10):
        self.id = bid
        self.x = x
        self.y = y
        self.radius = radius
        self.vx = 0
        self.vy = 0
        self.hp = 100
        self.stun_timer = 0.0
        self.alive = True

def test_time_stop_booster_collection():
    world = MockWorld()

    ball = MockBall(1, 500, 500)
    enemy = MockBall(2, 600, 600)
    world.balls = [ball, enemy]
    world.entities = world.balls

    time_stop_relic = MockHazard(99, 505, 505, "time_stop_booster", 10)
    world.boosters = [time_stop_relic]

    hazard = MockHazard(100, 700, 700, "hazard", 10)
    world.arena.hazards.append(hazard)

    action = Action(1, world)
    action.ball = ball

    # Run the tick to process booster collection
    action._collect_booster(0.1)

    # Validate the booster is consumed
    assert time_stop_relic not in world.boosters

    # Validate enemy is stunned
    assert getattr(enemy, "stun_timer", 0.0) >= 3.0

    # Validate hazard is frozen
    assert getattr(hazard, "frozen_timer", 0.0) >= 3.0

    # Validate event is triggered
    event_types = [e.get("type") for e in world.events]
    assert "time_stop" in event_types
