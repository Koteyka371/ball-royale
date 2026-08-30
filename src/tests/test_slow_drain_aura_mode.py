import pytest
import math
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id_val, x, y):
        self.id = id_val
        self.x = x
        self.y = y
        self.alive = True
        self.ball_type = "normal"
        self.stamina = 100.0

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

def test_slow_drain_aura():
    mode = GAME_MODES["slow_drain_aura"]
    world = MockWorld()

    # Calculate aura starting position (angle = 0)
    # aura_x = 500 + 300 = 800, aura_y = 500
    # b1 is inside the aura (dist < 150)
    b1 = MockBall(1, 800, 500)

    # b2 is outside the aura
    b2 = MockBall(2, 100, 100)

    balls = [b1, b2]
    mode.setup(world, balls)

    # Tick with delta 1.0 (should drain 10.0 stamina)
    mode.tick(world, balls, delta=1.0)

    assert abs(b1.stamina - 90.0) < 0.1
    assert abs(b2.stamina - 100.0) < 0.1

    # Check aura movement (angle increased)
    mode.tick(world, balls, delta=1.0)
    assert mode.aura_angle > 0.0
