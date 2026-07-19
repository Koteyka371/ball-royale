import pytest
from unittest.mock import MagicMock
from ai.game_modes import GameMode

def test_temperature_gauge_heatwave():
    mode = GameMode()
    world = MagicMock()
    world.arena = MagicMock()
    world.arena.weather = "heatwave"
    world.arena.temperature = 20.0
    world.arena.hazards = []

    ball = MagicMock()
    ball.alive = True
    ball.internal_temperature = 20.0
    ball.cooling_booster_timer = 0.0
    ball.hp = 100.0
    ball.speed = 100.0

    mode.apply_dynamic_traits(world, [ball], delta=1.0)

    # Arena temp moves towards 50.0
    assert world.arena.temperature > 20.0

    # Internal temp moves towards arena temp
    assert ball.internal_temperature > 20.0

def test_temperature_gauge_blizzard_and_freezing():
    mode = GameMode()
    world = MagicMock()
    world.arena = MagicMock()
    world.arena.weather = "blizzard"
    world.arena.temperature = -20.0
    world.arena.hazards = []

    ball = MagicMock()
    ball.alive = True
    ball.internal_temperature = -5.0
    ball.cooling_booster_timer = 0.0
    ball.hp = 100.0
    ball.speed = 100.0

    mode.apply_dynamic_traits(world, [ball], delta=1.0)

    # Internal temp moves towards -20.0
    assert ball.internal_temperature < -5.0
    # Speed reduced
    assert ball.speed == 0.0

def test_temperature_gauge_overheating_dot():
    mode = GameMode()
    world = MagicMock()
    world.arena = MagicMock()
    world.arena.weather = "heatwave"
    world.arena.temperature = 50.0
    world.arena.hazards = []

    ball = MagicMock()
    ball.alive = True
    ball.internal_temperature = 45.0
    ball.cooling_booster_timer = 0.0
    ball.hp = 100.0
    ball.speed = 100.0

    mode.apply_dynamic_traits(world, [ball], delta=1.0)

    # Internal temp stays high
    assert ball.internal_temperature > 40.0
    # Takes DoT
    assert ball.hp == 95.0

def test_temperature_gauge_lava_hazard():
    mode = GameMode()
    world = MagicMock()
    world.arena = MagicMock()
    world.arena.weather = "clear"
    world.arena.temperature = 20.0

    lava = MagicMock()
    lava.x = 0.0
    lava.y = 0.0
    lava.radius = 50.0
    lava.kind = "lava"
    world.arena.hazards = [lava]

    ball = MagicMock()
    ball.alive = True
    ball.x = 0.0
    ball.y = 0.0
    ball.internal_temperature = 20.0
    ball.cooling_booster_timer = 0.0
    ball.hp = 100.0
    ball.speed = 100.0

    mode.apply_dynamic_traits(world, [ball], delta=1.0)

    # Target temp becomes 60, so internal temp rises fast
    assert ball.internal_temperature > 20.0

def test_temperature_gauge_cooling_booster():
    mode = GameMode()
    world = MagicMock()
    world.arena = MagicMock()
    world.arena.weather = "heatwave"
    world.arena.temperature = 50.0
    world.arena.hazards = []

    ball = MagicMock()
    ball.alive = True
    ball.internal_temperature = 20.0
    ball.cooling_booster_timer = 5.0
    ball.hp = 100.0
    ball.speed = 100.0

    mode.apply_dynamic_traits(world, [ball], delta=1.0)

    # Target temp becomes -10 due to booster
    assert ball.internal_temperature < 20.0
