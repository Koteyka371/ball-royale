import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.action import Action

class MockBall:
    def __init__(self, id="p1", x=0, y=0, team="red"):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 10.0
        self.alive = True
        self.team = team

class MockBooster:
    def __init__(self, x=0, y=0, kind="echo_aura_booster"):
        self.x = x
        self.y = y
        self.radius = 10.0
        self.kind = kind
        self.active = True

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards or []

class MockWorld:
    def __init__(self, boosters=None, arena=None, balls=None):
        self.boosters = boosters or []
        self.arena = arena or MockArena()
        self.balls = balls or []

def test_echo_aura_booster_collection():
    ball = MockBall()
    booster = MockBooster(x=5, y=5)
    world = MockWorld(boosters=[booster], arena=MockArena(hazards=[booster]))
    action = Action(ball, world)
    action._get_boosters = lambda: [booster]

    action._collect_booster(0.1)

    assert getattr(ball, "echo_aura_timer", 0.0) == 5.0
    assert booster not in world.boosters
    assert booster not in world.arena.hazards

def test_echo_aura_effect():
    ball = MockBall(x=10, y=10)
    ball.echo_aura_timer = 5.0
    ball.speed_boost_timer = 10.0
    ball.shield_timer = 4.0
    ball.ghost_booster_timer = 0.0 # No ghost

    ally = MockBall(id="p2", x=20, y=10, team="red")
    enemy = MockBall(id="p3", x=15, y=10, team="blue")

    world = MockWorld(balls=[ball, ally, enemy])
    action = Action(ball, world)

    action._apply_friendly_aura(0.1)

    # Ally should get half duration of active buffs
    assert getattr(ally, "speed_boost_timer", 0.0) == 5.0
    assert getattr(ally, "shield_timer", 0.0) == 2.0
    assert getattr(ally, "ghost_booster_timer", 0.0) == 0.0

    # Enemy should not be affected
    assert getattr(enemy, "speed_boost_timer", 0.0) == 0.0
    assert getattr(enemy, "shield_timer", 0.0) == 0.0

if __name__ == "__main__":
    pytest.main([__file__])
