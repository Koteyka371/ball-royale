import pytest
from ai.game_modes import GAME_MODES, WeatherAltarsMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.weather = "clear"

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, bid, x, y):
        self.id = bid
        self.x = x
        self.y = y
        self.hp = 100.0
        self.max_hp = 100.0
        self.base_speed = 100.0
        self.speed = 100.0
        self.alive = True
        self.ball_type = "player"
        self.inventory = []

def test_weather_altars_mode_spawn():
    mode = GAME_MODES["weather_altars"]
    world = MockWorld()
    balls = [MockBall(1, 0, 0)]

    # clear weather -> no altars
    world.arena.weather = "clear"
    mode.tick(world, balls, 0.1)
    assert len(mode.altars) == 0

    # intense weather -> spawn altars
    world.arena.weather = "blizzard"
    mode.tick(world, balls, 0.1)
    assert len(mode.altars) == 1
    altar = mode.altars[0]
    assert "x" in altar
    assert "y" in altar

def test_weather_altars_purchase():
    mode = WeatherAltarsMode()
    world = MockWorld()

    # intense weather
    world.arena.weather = "thunderstorm"
    mode.tick(world, [], 0.1)
    assert len(mode.altars) == 1

    altar = mode.altars[0]
    # Place a ball exactly at the altar
    b = MockBall(1, altar["x"], altar["y"])

    # Tick for 1.9 seconds, shouldn't purchase yet
    for _ in range(19):
        mode.tick(world, [b], 0.1)

    assert 1 not in altar["purchased_by"]
    assert len(b.inventory) == 0
    assert b.max_hp == 100.0 and b.base_speed == 100.0

    # Tick 1 more time (2.0s total)
    mode.tick(world, [b], 0.1)

    assert 1 in altar["purchased_by"]
    assert len(b.inventory) == 1
    # Check if either max_hp or base_speed was reduced
    assert b.max_hp < 100.0 or b.base_speed < 100.0

def test_weather_altars_disappear_on_clear():
    mode = WeatherAltarsMode()
    world = MockWorld()

    world.arena.weather = "heatwave"
    mode.tick(world, [], 0.1)
    assert len(mode.altars) == 1

    world.arena.weather = "clear"
    mode.tick(world, [], 0.1)
    assert len(mode.altars) == 0
