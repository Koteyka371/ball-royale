import pytest
from ai.action import Action

class MockLeaderboardManager:
    def __init__(self, theme):
        self.season_theme = theme

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self, theme=""):
        self.arena = MockArena()
        self.time = 10.0
        if theme:
            self.leaderboard_manager = MockLeaderboardManager(theme)

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 100
        self.y = 100
        self.base_speed = 10.0
        self.speed = 10.0
        self.speed_boost_timer = 5.0

def test_speed_booster_fire_trail_default():
    world = MockWorld()
    ball = MockBall()
    action = Action(ball, world)

    # Mock random to always trigger trail
    import random
    original_random = random.random
    random.random = lambda: 0.1

    try:
        action.execute("idle", 0.016)
        assert len(world.arena.hazards) > 0
        hazard = world.arena.hazards[0]
        assert getattr(hazard, "kind", "") == "fire"
        assert getattr(hazard, "damage", 0) == 10.0
    finally:
        random.random = original_random

def test_speed_booster_ice_trail_frost_theme():
    world = MockWorld("Frost")
    ball = MockBall()
    action = Action(ball, world)

    # Mock random to always trigger trail
    import random
    original_random = random.random
    random.random = lambda: 0.1

    try:
        action.execute("idle", 0.016)
        assert len(world.arena.hazards) > 0
        hazard = world.arena.hazards[0]
        assert getattr(hazard, "kind", "") == "ice_patch"
        assert getattr(hazard, "damage", 10.0) == 0.0
        assert getattr(hazard, "duration", 0) == 3.0
    finally:
        random.random = original_random
