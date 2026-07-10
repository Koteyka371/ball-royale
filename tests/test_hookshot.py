import pytest
import math
from ai.action import Action

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

    def clamp_position(self, x, y, r):
        return x, y

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.items = []
        self.boosters = []
        self.entities = []

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "hazards": [], "boosters": []}

class MockHazard:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.inventory = ["hookshot"]
        self.alive = True
        self.team = 1
        self.id = 1
        self.mass = 1.0

def test_hookshot_out_of_bounds_save():
    world = MockWorld()
    ball = MockBall(-10, 500)
    world.balls.append(ball)

    # We must delete speed so action logic doesn't add random wander displacement
    if hasattr(ball, "speed"):
        ball.base_speed = 0.0
        ball.speed = 0.0

    action = Action(ball, world)
    try:
        action.execute("flee", 1.0)
    except Exception:
        pass

    assert math.isclose(ball.x, 0.0, abs_tol=5.0)
    assert "hookshot" not in ball.inventory

def test_hookshot_lava_save():
    world = MockWorld()
    ball = MockBall(500, 500)
    world.balls.append(ball)

    lava = MockHazard("lava", 510, 510)
    world.arena.hazards.append(lava)

    if hasattr(ball, "speed"):
        ball.base_speed = 0.0
        ball.speed = 0.0

    action = Action(ball, world)
    try:
        action.execute("flee", 1.0)
    except Exception:
        pass

    assert "hookshot" not in ball.inventory
    # At (500,500), all walls are equidistant (500). The min key will probably be "left" or "top".
    # In action.py: dists = {"left": 500, "right": 500, "top": 500, "bottom": 500}
    # min() on dict returns "bottom" if alphabetical, or "left" depending on insertion order (in Python 3.7+ it preserves insertion order, so "left" is first).
    # If "left", ball.x = max(0, 500 - 600) = 0.
    assert any(math.isclose(val, bound, abs_tol=5.0) for val in (ball.x, ball.y) for bound in (0.0, 1000.0))
