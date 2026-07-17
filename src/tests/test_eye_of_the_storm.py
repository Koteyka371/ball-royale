import pytest
import math
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.weather = "clear"
        self.name = "default"

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 50.0
        self.max_hp = 100.0
        self.alive = True
        self.ball_type = "basic"
        self.weather_immunity_timer = 0.0

def test_eye_of_the_storm_healing():
    mode = GAME_MODES.get("eye_of_the_storm")
    assert mode is not None

    world = MockWorld()
    # Ball 1 inside eye
    b1 = MockBall(1, 500, 500)
    # Ball 2 outside eye, but in safe zone
    b2 = MockBall(2, 500, 700)

    mode.setup(world, [b1, b2])

    # Force eye position
    mode.eye_x = 500
    mode.eye_y = 500
    mode.eye_radius = 100

    mode.tick(world, [b1, b2], delta=1.0)

    assert b1.hp == 100.0 # 50 + 50 heal rate
    assert b2.hp == 50.0  # untouched
