import pytest
import sys
import os

# Add src directory to PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from src.ai.game_modes import WeatherChaosMode

class MockBall:
    def __init__(self):
        self.alive = True
        self.ball_type = "normal"
        self.speed = 100.0
        self.damage = 10.0
        self.x = 500.0
        self.y = 500.0

class MockWorld:
    def __init__(self):
        self.dead_balls = []

def test_weather_chaos_wind_east():
    mode = WeatherChaosMode()
    mode.weather = "wind_east"
    ball = MockBall()
    mode.tick(MockWorld(), [ball], delta=0.1)
    assert ball.x > 500.0
    assert ball.y == 500.0

def test_weather_chaos_wind_west():
    mode = WeatherChaosMode()
    mode.weather = "wind_west"
    ball = MockBall()
    mode.tick(MockWorld(), [ball], delta=0.1)
    assert ball.x < 500.0
    assert ball.y == 500.0

def test_weather_chaos_storm():
    mode = WeatherChaosMode()
    mode.weather = "storm"
    ball = MockBall()
    mode.tick(MockWorld(), [ball], delta=0.1)
    assert ball.x != 500.0 or ball.y != 500.0
