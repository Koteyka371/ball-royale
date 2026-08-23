import pytest
from ai.game_modes import GAME_MODES

def test_extreme_weather_zones_mode():
    mode = GAME_MODES["extreme_weather_zones"]

    # Mock world
    world = type('MockWorld', (), {})()
    world.arena = type('MockArena', (), {'width': 1000.0, 'height': 1000.0})()

    # Mock ball
    b1 = type('MockBall', (), {'x': 500.0, 'y': 500.0, 'hp': 100, 'base_speed': 100.0, 'speed': 100.0, 'radius': 20.0, 'weather_zone_timer': 0.0, 'weather_slowed': False})()

    balls = [b1]

    mode.setup(world, balls)
    assert len(mode.weather_zones) == 0

    # Inject a weather zone manually
    mode.weather_zones.append({
        "x": 500.0,
        "y": 500.0,
        "radius": 150.0,
        "duration": 10.0
    })

    # Tick for 2.0 seconds
    for _ in range(20):
        mode.tick(world, balls, 0.1)

    assert b1.weather_zone_timer > 1.9
    assert b1.weather_zone_timer < 2.1
    assert getattr(b1, "weather_slowed", False) == False
    assert b1.hp == 100

    # Tick for another 1.5 seconds (total 3.5 > 3.0)
    for _ in range(15):
        mode.tick(world, balls, 0.1)

    assert b1.weather_zone_timer > 3.4
    assert b1.weather_slowed == True
    assert b1.hp < 100

    # Move ball out of zone
    b1.x = 1000.0
    mode.tick(world, balls, 0.1)

    assert b1.weather_zone_timer == 0.0
    assert getattr(b1, "weather_slowed", False) == False
