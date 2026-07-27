import pytest
from src.ai.game_modes import DynamicCaptureZoneMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.tick_timer = 0
        self.dead_balls = []
        self.boosters = []

class MockBall:
    def __init__(self, id_val, team, x, y):
        self.id = id_val
        self.team = team
        self.ball_type = "player"
        self.alive = True
        self.x = x
        self.y = y
        self.score = 0

def test_dynamic_capture_zone_scoring():
    mode = DynamicCaptureZoneMode()
    world = MockWorld()

    b1 = MockBall(1, "Red", 500, 500)
    b2 = MockBall(2, "Red", 500, 500)
    balls = [b1, b2]

    mode.setup(world, balls)

    # Tick with only Red in zone
    mode.tick(world, balls, delta=1.0)

    assert b1.score > 0
    assert b2.score > 0

def test_dynamic_capture_zone_contested():
    mode = DynamicCaptureZoneMode()
    world = MockWorld()

    b1 = MockBall(1, "Red", 500, 500)
    b2 = MockBall(2, "Blue", 500, 500)
    balls = [b1, b2]

    mode.setup(world, balls)

    # Tick with both in zone (contested)
    mode.tick(world, balls, delta=1.0)

    assert b1.score == 0
    assert b2.score == 0

def test_dynamic_capture_zone_moves():
    mode = DynamicCaptureZoneMode()
    world = MockWorld()

    balls = []
    mode.setup(world, balls)

    initial_x = mode.zone_x
    initial_y = mode.zone_y

    # Force target far away
    mode.target_x = 900
    mode.target_y = 900

    mode.tick(world, balls, delta=1.0)

    assert mode.zone_x != initial_x or mode.zone_y != initial_y
