import pytest
import sys
import os

sys.path.append("src")
from ai.game_modes import TricksterEventMode

class MockBall:
    def __init__(self, ball_type="tank"):
        self.alive = True
        self.team = "A"
        self.ball_type = ball_type
        self.traits = []

def test_trickster_event_mode():
    mode = TricksterEventMode()
    b1 = MockBall("tank")
    b2 = MockBall("healer")
    balls = [b1, b2]

    class MockWorld:
        pass

    world = MockWorld()

    mode.setup(world, balls)
    mode.tick(world, balls, 0.0)

    assert b1.ball_type == "trickster"
    assert b2.ball_type == "trickster"

    mode.tick(world, balls, 31.0)

    assert b1.ball_type == "tank"
    assert b2.ball_type == "healer"
