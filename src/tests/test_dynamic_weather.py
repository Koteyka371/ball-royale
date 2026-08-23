import pytest
from unittest.mock import MagicMock
from ai.game_modes import BattleRoyaleMode

class MockLeaderboardManager:
    def __init__(self, season):
        self.data = {"current_season": season}

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []
        self.is_foggy = False
        self.is_raining = False
        self.is_sandstorming = False
        self.is_snowing = False
        self.is_heatwave = False
        self.is_hailing = False
        self.is_acid_raining = False
        self.is_lunar_eclipse = False
        self.is_eclipse = False
        self.wind_dx = 0.0
        self.wind_dy = 0.0

class MockWorld:
    def __init__(self, season):
        self.leaderboard_manager = MockLeaderboardManager(season)
        self.arena = MockArena()
        self.boosters = []
        self.dead_balls = []

def test_dynamic_weather_winter():
    mode = BattleRoyaleMode()
    world = MockWorld(season=4) # Winter

    # Tick to trigger weather change
    mode.weather_timer = 11.0
    mode.tick(world, [], 1.0)

    assert mode.weather in ["clear", "snow", "blizzard", "fog", "wind"]

def test_dynamic_weather_summer():
    mode = BattleRoyaleMode()
    world = MockWorld(season=2) # Summer

    mode.weather_timer = 11.0
    mode.tick(world, [], 1.0)

    assert mode.weather in ["clear", "heatwave", "sandstorm", "wind", "thunderstorm"]
