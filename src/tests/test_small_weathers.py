import sys
import os

# Ensure src is in the path for testing
sys.path.append('src')

from ai.game_modes import GameMode

class MockArena:
    def __init__(self, weather="clear"):
        self.weather = weather
        self.temperature = 20.0
        self.name = "normal"
        self.hazards = []

class MockWorld:
    def __init__(self, weather="clear"):
        self.arena = MockArena(weather)

class MockBall:
    def __init__(self, ball_type="normal", hp=100.0, speed=100.0, defense_multiplier=1.0):
        self.ball_type = ball_type
        self.traits = []
        self.hp = hp
        self.max_hp = 100.0
        self.speed = speed
        self.base_speed = speed
        self.defense_multiplier = defense_multiplier
        self.alive = True
        self.x = 0.0
        self.y = 0.0

def test_wind_in_breeze():
    gm = GameMode()
    world = MockWorld(weather="slight_breeze")
    b = MockBall(ball_type="wind")
    gm.apply_dynamic_traits(world, [b], 1.0)
    assert abs(b.speed - 120.0) < 0.01

def test_wind_in_hurricane():
    gm = GameMode()
    world = MockWorld(weather="hurricane")
    b = MockBall(ball_type="wind")
    gm.apply_dynamic_traits(world, [b], 1.0)
    assert abs(b.x - 100.0) < 0.01
    assert abs(b.y - 100.0) < 0.01
    assert abs(b.defense_multiplier - 1.5) < 0.01

def test_water_in_light_rain():
    gm = GameMode()
    world = MockWorld(weather="light_rain")
    b = MockBall(ball_type="water", hp=50.0)
    gm.apply_dynamic_traits(world, [b], 1.0)
    assert abs(b.speed - 110.0) < 0.01
    assert abs(b.hp - 55.0) < 0.01
