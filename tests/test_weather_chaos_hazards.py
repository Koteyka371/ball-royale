import pytest
from src.ai.game_modes import WeatherChaosMode

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000
        self.is_foggy = False
        self.is_raining = False
        self.is_sandstorming = False
        self.is_snowing = False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []

def test_weather_chaos_hazards():
    mode = WeatherChaosMode()
    world = MockWorld()

    # Force weather to wind
    mode.weather = "wind"
    mode.weather_timer = 0.0

    # Mock random to always spawn hazard
    class MockRandom:
        def random(self):
            return 0.0 # Force spawn
        def uniform(self, a, b):
            return a
        def randint(self, a, b):
            return a
        def choice(self, seq):
            return seq[0]

    mode.random = MockRandom()

    mode.tick(world, [], delta=1.0)

    # Should have spawned a tornado
    assert len(world.arena.hazards) > 0
    assert world.arena.hazards[0].kind == "tornado"

    # Clear hazards
    world.arena.hazards = []

    # Force weather to thunderstorm
    mode.weather = "thunderstorm"
    mode.tick(world, [], delta=1.0)

    # Should have spawned lightning strike
    assert len(world.arena.hazards) > 0
    assert world.arena.hazards[0].kind == "lightning_warning"
