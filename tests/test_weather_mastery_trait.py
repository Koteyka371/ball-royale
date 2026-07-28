import pytest
from ai.game_modes import GameMode

class MockArena:
    def __init__(self, weather="clear"):
        self.weather = weather
        self.hazards = []

class MockWorld:
    def __init__(self, weather="clear"):
        self.arena = MockArena(weather)

class MockBall:
    def __init__(self, traits=None, mutated_env=None):
        self.alive = True
        self.ball_type = "default"
        self.traits = traits or []
        self.mutated_env = mutated_env
        self.base_speed = 100.0
        self.speed = 100.0
        self.defense_multiplier = 1.0

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __contains__(self, key):
        return hasattr(self, key)

    def get(self, key, default=None):
        return getattr(self, key, default)

def test_weather_mastery_no_extreme_weather():
    mode = GameMode()
    world = MockWorld(weather="clear")
    ball = MockBall(traits=["weather_mastery"])

    mode.apply_dynamic_traits(world, [ball], 0.016)

    assert ball.speed == 100.0
    assert ball.defense_multiplier == 1.0

def test_weather_mastery_extreme_weather_hurricane():
    mode = GameMode()
    world = MockWorld(weather="hurricane")
    ball = MockBall(traits=["weather_mastery"])

    mode.apply_dynamic_traits(world, [ball], 0.016)

    assert ball.speed == 120.0
    assert ball.defense_multiplier == 0.8

def test_weather_mastery_extreme_weather_blizzard():
    mode = GameMode()
    world = MockWorld(weather="blizzard")
    ball = MockBall(traits=["weather_mastery"])

    mode.apply_dynamic_traits(world, [ball], 0.016)

    assert ball.speed == 120.0
    assert ball.defense_multiplier == 0.8

def test_weather_mastery_in_hazard():
    mode = GameMode()
    world = MockWorld(weather="clear")
    ball = MockBall(traits=["weather_mastery"], mutated_env="mud_puddle")

    mode.apply_dynamic_traits(world, [ball], 0.016)

    assert ball.speed == 120.0
    assert ball.defense_multiplier == 0.8

def test_no_trait_extreme_weather():
    mode = GameMode()
    world = MockWorld(weather="hurricane")
    ball = MockBall(traits=["other_trait"])

    mode.apply_dynamic_traits(world, [ball], 0.016)

    assert ball.speed == 100.0
    assert ball.defense_multiplier == 1.0
