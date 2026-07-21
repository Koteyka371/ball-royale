import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, team, x, y):
        self.team = team
        self.ball_type = team
        self.x = x
        self.y = y
        self.alive = True
        self.speed = 100.0
        self.stamina = 100.0
        self.max_stamina = 100.0

def test_weather_combinations_mode_logic():
    mode = GAME_MODES['weather_combinations']
    world = MockWorld()

    b1 = MockBall("red", 250.0, 250.0) # at rain altar
    b2 = MockBall("blue", 750.0, 750.0) # at heatwave altar
    balls = [b1, b2]

    mode.setup(world, balls)

    assert len(mode.altars) == 2

    # Tick to capture altars
    for _ in range(100):
        mode.tick(world, balls, 0.1)

    assert "steam" == mode.combined_weather

    # Check stamina drain and speed change
    assert b1.stamina < 100.0
    assert b1.speed < 100.0
