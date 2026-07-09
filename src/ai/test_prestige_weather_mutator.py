import pytest
from ai.game_modes import PrestigeWeatherMutatorMode

class MockProfileManager:
    def __init__(self, prestige=0):
        self.data = {"prestige_level": prestige}

class MockWorld:
    def __init__(self, prestige=0):
        self.profile_manager = MockProfileManager(prestige)

class MockBall:
    def __init__(self, alive=True, immune=0.0):
        self.alive = alive
        self.weather_immunity_timer = immune
        self.hp = 100.0

def test_prestige_weather_setup_low_prestige():
    mode = PrestigeWeatherMutatorMode()
    world = MockWorld(prestige=3)
    balls = []
    mode.setup(world, balls)

    assert mode.lobby_prestige == 3
    assert "solar_flare" not in mode.weathers
    assert "clear" in mode.weathers

def test_prestige_weather_setup_high_prestige():
    mode = PrestigeWeatherMutatorMode()
    world = MockWorld(prestige=5)
    balls = []
    mode.setup(world, balls)

    assert mode.lobby_prestige == 5
    assert "solar_flare" in mode.weathers

def test_prestige_weather_setup_very_high_prestige():
    mode = PrestigeWeatherMutatorMode()
    world = MockWorld(prestige=10)
    balls = []
    mode.setup(world, balls)

    assert mode.lobby_prestige == 10
    assert "solar_flare" in mode.weathers

def test_prestige_weather_tick():
    mode = PrestigeWeatherMutatorMode()
    world = MockWorld(prestige=10)
    b1 = MockBall(alive=True, immune=0.0)
    b2 = MockBall(alive=True, immune=0.0)

    b3 = MockBall(alive=False, immune=0.0)
    balls = [b1, b2, b3]

    mode.setup(world, balls)
    mode.weather = "solar_flare"
    b2.weather_immunity_timer = 5.0

    mode.tick(world, balls, delta=1.0)

    assert b1.hp == 90.0
    assert b2.hp == 100.0
    assert b3.hp == 100.0
