import pytest
import sys
from unittest.mock import Mock
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id, x, y, hp):
        self.id = id
        self.x = x
        self.y = y
        self.hp = hp
        self.alive = True
        self.ball_type = "player"

class MockWorld:
    pass

def test_reverse_time_penalty():
    mode = GAME_MODES['reverse_time_penalty']
    assert mode.name == "Reverse Time Penalty"

    world = MockWorld()
    b1 = MockBall("b1", 100.0, 100.0, 100.0)
    balls = [b1]

    # Advance time to t=49
    for _ in range(49):
        mode.tick(world, balls, delta=1.0)

    # At t=50, b1 is at (150, 150)
    b1.x = 150.0
    b1.y = 150.0
    mode.tick(world, balls, delta=1.0) # t=50

    b1.x = 200.0
    b1.y = 200.0

    for _ in range(9):
        mode.tick(world, balls, delta=1.0) # t=51 to 59

    assert mode.timer == 59.0
    b1.hp = 20.0

    mode.tick(world, balls, delta=1.0) # t=60

    # Position should be rewound to what it was at t=50 (150, 150)
    assert b1.x == 150.0
    assert b1.y == 150.0

    # HP should remain at 20.0 (current levels)
    assert b1.hp == 20.0

    # History and timer should be reset
    assert mode.timer == 0.0
    assert len(mode.history) == 0
