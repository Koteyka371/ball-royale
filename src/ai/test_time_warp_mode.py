import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, bid, x, y, hp):
        self.id = bid
        self.x = x
        self.y = y
        self.hp = hp

class MockWorld:
    pass

def test_time_warp_mode():
    mode = GAME_MODES["time_warp"]
    world = MockWorld()
    b1 = MockBall(1, 10.0, 10.0, 100.0)
    balls = [b1]

    # Tick for 5 seconds to record state
    for _ in range(500):
        mode.tick(world, balls, delta=0.01)

    # Modify state
    # Fast forward to just before 30s
    for _ in range(2490):
        mode.tick(world, balls, delta=0.01)

    # Modify state right before rewind
    b1.x = 20.0
    b1.y = 20.0
    b1.hp = 50.0

    # Last few ticks to hit 30s
    for _ in range(10):
        mode.tick(world, balls, delta=0.01)

    # The last tick should have triggered rewind
    assert b1.x == 10.0
    assert b1.hp == 100.0
