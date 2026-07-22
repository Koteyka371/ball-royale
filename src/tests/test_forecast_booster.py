import sys
sys.path.append("src")
import pytest
from ai.game_modes import ExtremeWeatherMode, DynamicWeatherTransitionsMode, WeatherChaosMode

class MockArena:
    def __init__(self):
        self.weather = "clear"

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.altars = [{"owner": None}]

    def add_event(self, name, data):
        self.events.append((name, data))

class MockBall:
    def __init__(self):
        self.alive = True
        self.speed = 100.0
        self.base_speed = 100.0
        self.id = 1
        self.forecast_booster_active = True
        self.forecast_warning_issued = False
        self.ball_type = "normal"

def test_forecast_extreme_weather_warning():
    mode = ExtremeWeatherMode()
    world = MockWorld()
    ball = MockBall()
    balls = [ball]

    mode.setup(world, balls)

    # ExtremeWeatherMode cycles every 15s. At 15-10=5s, a warning should trigger
    mode.weather_timer = 5.0
    mode.tick(world, balls, delta=0.1)

    assert getattr(ball, 'forecast_warning_issued', False) == True
    assert any(e[0] == "weather_warning" and "Forecast warns" in e[1]["message"] for e in world.events)


def test_forecast_extreme_weather_consume():
    mode = ExtremeWeatherMode()
    world = MockWorld()
    ball = MockBall()
    balls = [ball]

    mode.setup(world, balls)
    mode.weather_timer = 14.9
    mode.tick(world, balls, delta=0.2)

    assert mode.weather_timer < 1.0 # Resets after 15.0
    assert getattr(ball, 'forecast_booster_active', True) == False
    assert getattr(ball, "weather_immunity_timer", 0.0) == 15.0


def test_forecast_dynamic_transitions():
    mode = DynamicWeatherTransitionsMode()
    world = MockWorld()
    ball = MockBall()
    balls = [ball]

    mode.setup(world, balls)
    # Transitions happen every 20s. Warning at 10s left.
    mode.weather_timer = 10.0
    mode.tick(world, balls, delta=0.1)

    assert getattr(ball, 'forecast_warning_issued', False) == True
    assert any(e[0] == "weather_warning" and "Forecast warns" in e[1]["message"] for e in world.events)

def test_forecast_dynamic_transitions_consume():
    mode = DynamicWeatherTransitionsMode()
    world = MockWorld()
    ball = MockBall()
    balls = [ball]

    mode.setup(world, balls)
    mode.weather_timer = 0.1
    mode.tick(world, balls, delta=0.2)

    assert getattr(ball, 'forecast_booster_active', True) == False
    assert getattr(ball, "weather_immunity_timer", 0.0) == 15.0
    assert getattr(ball, "aura_booster_timer", 0.0) == 15.0
