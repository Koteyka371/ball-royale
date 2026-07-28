import pytest
from ai.action import Action
import random

class MockWorld:
    def __init__(self, arena, balls=None, boosters=None):
        self.arena = arena
        self.balls = balls or []
        self.boosters = boosters or []
        self.events = []

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": [], "boosters": self.boosters, "hazards": self.arena.hazards}

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards

class MockBall:
    def __init__(self, x, y, id=1, team=1):
        self.x = x
        self.y = y
        self.id = id
        self.team = team
        self.radius = 10
        self.speed = 100
        self.vx = 0
        self.vy = 0
        self.inventory = []

    def __getitem__(self, key):
        return getattr(self, key)
    def __setitem__(self, key, value):
        setattr(self, key, value)
    def get(self, key, default=None):
        return getattr(self, key, default)
    def __contains__(self, key):
        return hasattr(self, key)

class MockHazard:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 10

    def __getitem__(self, key):
        return getattr(self, key)
    def get(self, key, default=None):
        return getattr(self, key, default)

def test_hazard_jar_store_and_deploy():
    jar = MockHazard(10, 10, "hazard_jar_item")
    hazard1 = MockHazard(12, 12, "acid_puddle")
    hazard2 = MockHazard(100, 100, "fire_zone")

    world = MockWorld(MockArena([jar, hazard1, hazard2]), boosters=[jar])
    ball = MockBall(10, 10)
    ball.skill_timer = 0.0
    world.balls.append(ball)

    action = Action(ball, world)

    # 1. Collect
    action._collect_booster(0.1)
    assert jar not in world.boosters
    assert jar not in world.arena.hazards
    assert len(ball.inventory) == 1
    assert ball.inventory[0]["item"] == "hazard_jar_item"
    assert ball.inventory[0]["stored_hazard"] is None

    # 2. Store hazard
    action._use_skill()
    assert ball.inventory[0]["stored_hazard"] == "acid_puddle"
    assert hazard1 not in world.arena.hazards
    assert hazard2 in world.arena.hazards

    # 3. Deploy hazard
    ball.x = 50
    ball.y = 50
    action._use_skill()
    assert len(ball.inventory) == 0
    assert len(world.arena.hazards) == 2
    new_hazard = world.arena.hazards[-1]
    assert new_hazard.kind == "acid_puddle"
    assert new_hazard.x == 50
    assert new_hazard.y == 50
    assert new_hazard.owner_id == ball.id
