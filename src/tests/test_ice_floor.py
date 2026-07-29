import pytest
from ai.game_modes import GAME_MODES

def test_ice_floor_mode():
    assert "ice_floor" in GAME_MODES
    mode = GAME_MODES["ice_floor"]

    class MockWorld:
        def __init__(self):
            self.dead_balls = []

    class MockBall:
        def __init__(self):
            self.alive = True
            self.ball_type = "player"
            self.is_frictionless = False
            self.friction_multiplier = 1.0
            self.max_speed = 100.0

    b = MockBall()
    w = MockWorld()

    mode.tick(w, [b], 0.016)

    assert b.is_frictionless is True
    assert b.friction_multiplier == 0.0
    assert b.max_speed == 99999.0
