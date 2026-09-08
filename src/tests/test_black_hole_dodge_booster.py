import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.action import Action

class MockBall:
    def __init__(self, id="p1", x=0, y=0):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.radius = 10.0
        self.alive = True
        self.is_dashing = False
        self.dash_range_mult = 1.0
        self.active_skill = "dash"
        self.skill = "dash"

class MockBooster:
    def __init__(self, x=0, y=0, kind="black_hole_dodge_booster"):
        self.x = x
        self.y = y
        self.radius = 10.0
        self.kind = kind
        self.active = True

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards or []

class MockWorld:
    def __init__(self, boosters=None, arena=None):
        self.boosters = boosters or []
        self.arena = arena or MockArena()
        self.events = []
        self.projectiles = []
        self.balls = []

def test_black_hole_dodge_booster_collection():
    ball = MockBall()
    booster = MockBooster(x=5, y=5)
    world = MockWorld(boosters=[booster], arena=MockArena(hazards=[booster]))
    action = Action(ball, world)
    action._get_boosters = lambda: [booster]

    action._collect_booster(0.1)

    assert getattr(ball, "has_black_hole_dodge_booster", False) is True
    assert booster not in world.boosters
    assert booster not in world.arena.hazards

def test_black_hole_dodge_booster_effect():
    ball = MockBall()
    ball.has_black_hole_dodge_booster = True
    world = MockWorld(arena=MockArena())
    action = Action(ball, world)

    # Need to simulate skill to execute the effect
    ball.skill_timer = 0.0
    action.execute("use_skill", 0.1)

    assert getattr(ball, "has_black_hole_dodge_booster", False) is False
    assert any(h.kind == "mini_black_hole" for h in world.arena.hazards)

if __name__ == "__main__":
    pytest.main([__file__])
