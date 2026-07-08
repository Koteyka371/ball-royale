import pytest
from ai.game_modes import WeatherChaosMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.is_raining = False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, team, x, y):
        self.ball_type = team
        self.team = team
        self.x = x
        self.y = y
        self.alive = True
        self.perception_radius = 250.0
        self.speed = 100.0
        self.damage = 10.0
        self.weather_immunity_timer = 0.0

def test_weather_chaos_altar_capture():
    mode = WeatherChaosMode()
    world = MockWorld()

    # Place a swamp ball right at the center where the altar spawns
    b1 = MockBall("swamp", 500, 500)

    mode.setup(world, [b1])

    assert hasattr(mode, "altars")
    assert len(mode.altars) == 1
    altar = mode.altars[0]

    assert altar["owner"] is None
    assert altar["capture_progress"] == 0.0

    # Tick loop to capture the altar
    delta = 0.1
    for _ in range(60): # 6 seconds should be enough to capture (decay doesn't happen because it's populated)
        mode.tick(world, [b1], delta)
        if mode.weather == "rain":
            break

    assert altar["owner"] == "swamp"
    assert mode.weather == "rain"

def test_weather_chaos_altar_decay():
    mode = WeatherChaosMode()
    world = MockWorld()

    # Nobody at center initially
    b1 = MockBall("swamp", 100, 100) # Far away from 500, 500

    mode.setup(world, [b1])
    altar = mode.altars[0]

    # Manually give some progress and owner
    altar["owner"] = "swamp"
    altar["capture_progress"] = 50.0

    # Tick loop to decay
    delta = 0.1
    mode.tick(world, [b1], delta)

    assert altar["capture_progress"] < 50.0
