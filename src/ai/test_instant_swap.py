import pytest
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self, balls):
        self.arena = MockArena()
        self.balls = balls
        self.entities = balls
        self.events = []

class MockBall:
    def __init__(self, id, x, y, team=""):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.skill_timer = 0.0
        self.skill = "instant_swap"
        self.SKILL_COOLDOWN = 4.0

class MockHazard:
    def __init__(self, id, x, y, kind):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.duration = 1.0
        self.radius = 10.0
        self.active = False

    def __contains__(self, key):
        return hasattr(self, key)
    def get(self, key, default=None):
        return getattr(self, key, default)
    def __setitem__(self, key, value):
        setattr(self, key, value)
    def __getitem__(self, key):
        return getattr(self, key)

def test_instant_swap_with_enemy():
    b1 = MockBall(1, 100, 100, "A")
    b2 = MockBall(2, 200, 200, "B")
    world = MockWorld([b1, b2])
    action = Action(b1, world)
    action._use_skill()
    assert b1.x == 200
    assert b1.y == 200
    assert b2.x == 100
    assert b2.y == 100

def test_instant_swap_with_hazard():
    b1 = MockBall(1, 100, 100, "A")
    b2 = MockBall(2, 500, 500, "B") # Far away
    h = MockHazard(3, 150, 150, "test_hazard")
    world = MockWorld([b1, b2])
    world.arena.hazards.append(h)
    action = Action(b1, world)
    action._use_skill()
    assert b1.x == 150
    assert b1.y == 150
    assert h.x == 100
    assert h.y == 100
    assert getattr(h, 'active', False) or getattr(h, 'duration', 0.0) >= 2.0
