import random
import pytest
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.time = 0.0

class MockLeaderboard:
    def __init__(self, theme):
        self.theme = theme
        self.data = {"current_season": 1}
    def get_theme(self, season):
        return self.theme

class MockBall:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.speed_boost_timer = 5.0
        self.base_speed = 2.0
        self.speed = 2.0
        self.id = 1
        self.ball_type = "base"

def test_frost_speed_booster():
    world = MockWorld()
    world.leaderboard_manager = MockLeaderboard("Frost")
    b = MockBall()
    action = Action(b, world)
    random.seed(42)
    for _ in range(10):
        action.execute("idle", 0.1)

    assert len(world.arena.hazards) > 0
    assert all(h.kind == "ice_patch" for h in world.arena.hazards)
    assert all(h.duration == 3.0 for h in world.arena.hazards if h.kind == "ice_patch")
    assert all(h.damage == 0.0 for h in world.arena.hazards if h.kind == "ice_patch")

def test_genesis_speed_booster():
    world = MockWorld()
    world.leaderboard_manager = MockLeaderboard("Genesis")
    b = MockBall()
    action = Action(b, world)
    random.seed(42)
    for _ in range(10):
        action.execute("idle", 0.1)

    assert len(world.arena.hazards) > 0
    assert all(h.kind == "fire" for h in world.arena.hazards)
    assert all(h.duration == 2.0 for h in world.arena.hazards if h.kind == "fire")
    assert all(h.damage == 10.0 for h in world.arena.hazards if h.kind == "fire")
