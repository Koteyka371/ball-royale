import sys
import pytest
sys.path.append("src")
from ai.ball_types_meteorologist import Meteorologist
from ai.game_modes import ExtremeWeatherMode

class MockArena:
    pass

class MockWorld:
    def __init__(self):
        self.events = []
        self.arena = MockArena()
    def add_event(self, type, data):
        self.events.append((type, data))

def test_meteorologist_init():
    m = Meteorologist(1)
    assert m.BALL_TYPE == "meteorologist"
    assert m.forecast_booster_active == True
    assert m.forecast_warning_issued == False

def test_meteorologist_in_weather_mode():
    world = MockWorld()
    mode = ExtremeWeatherMode()
    m = Meteorologist(1)

    # Tick near weather change
    mode.weather_timer = 12.0
    mode.tick(world, [m], 0.1)

    # Should get warning because it's <= 10s until change (15s total)
    assert m.forecast_warning_issued == True
    warnings = [e for e in world.events if e[0] == "weather_warning"]
    assert len(warnings) > 0
    assert "Forecast warns" in warnings[0][1]["message"]

    # Fast forward to weather change
    mode.weather_timer = 15.1
    mode.tick(world, [m], 0.1)

    # In ExtremeWeatherMode, forecast_booster_active gets reset to False after use.
    # The meteorologist skill should re-enable it.
    m.skill_timer = 0
    assert m.use_skill() == True
    assert m.forecast_booster_active == True
