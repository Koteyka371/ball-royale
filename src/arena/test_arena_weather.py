import pytest
from arena.procedural_arena import ProceduralArena
from arena.arena_types import WinterArena, SummerArena

def test_procedural_arena_weather_trigger():
    arena = ProceduralArena()
    arena.update_zone(0, 0.1)
    assert getattr(arena, "weather", "") == "clear"

    arena._trigger_event("blizzard", 1)
    assert arena.weather == "blizzard"
    assert arena.weather_timer == 20.0

    arena.update_zone(2, 10.0)
    assert arena.weather == "blizzard"
    assert arena.weather_timer == 10.0

    arena.update_zone(3, 10.0)
    assert arena.weather == "clear"
    assert arena.weather_timer <= 0.0

def test_summer_arena_weather():
    arena = SummerArena()
    arena.update_zone(0, 0.1)
    # SummerArena might have heatwave initially

    arena._trigger_event("heatwave", 1)
    assert arena.weather == "heatwave"
    assert arena.weather_timer == 15.0
