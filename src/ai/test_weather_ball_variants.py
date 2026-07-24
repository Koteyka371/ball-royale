import pytest
from ai.game_modes import GameMode
from ai.ball_types_snowball import Snowball
from ai.ball_types_sandball import Sandball
from ai.ball_types_thunderball import Thunderball

class MockArena:
    def __init__(self, weather="clear"):
        self.weather = weather
        self.hazards = []

class MockWorld:
    def __init__(self, weather="clear"):
        self.arena = MockArena(weather)
        self.gravity_reversal_active = False
        self.gravity_reversal_timer = 0.0

def test_weather_ball_buffs():
    mode = GameMode()
    snowball = Snowball(1, 0, 0)
    sandball = Sandball(2, 0, 0)
    thunderball = Thunderball(3, 0, 0)
    balls = [snowball, sandball, thunderball]

    # Test no buff on clear weather
    world = MockWorld("clear")
    mode.apply_dynamic_traits(world, balls, 0.1)
    assert snowball.speed == snowball.base_speed
    assert sandball.speed == sandball.base_speed
    assert thunderball.speed == thunderball.base_speed

    # Test blizzard buffs snowball
    world.arena.weather = "blizzard"
    mode.apply_dynamic_traits(world, balls, 0.1)
    assert snowball.speed > snowball.base_speed
    assert sandball.speed == sandball.base_speed
    assert thunderball.speed == thunderball.base_speed

    # Test sandstorm buffs sandball
    world.arena.weather = "sandstorm"
    mode.apply_dynamic_traits(world, balls, 0.1)
    assert snowball.speed == snowball.base_speed
    assert sandball.speed > sandball.base_speed
    assert thunderball.speed == thunderball.base_speed

    # Test thunderstorm buffs thunderball
    world.arena.weather = "thunderstorm"
    mode.apply_dynamic_traits(world, balls, 0.1)
    assert snowball.speed == snowball.base_speed
    assert sandball.speed == sandball.base_speed
    assert thunderball.speed > thunderball.base_speed
