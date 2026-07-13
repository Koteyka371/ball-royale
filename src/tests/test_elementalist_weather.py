import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ai.game_modes import GameMode
from unittest.mock import MagicMock

class MockBall:
    def __init__(self, ball_type="elementalist"):
        self.ball_type = ball_type
        self.traits = ["elemental"]
        self.speed = 100.0
        self.base_speed = 100.0
        self.defense_multiplier = 1.0
        self.alive = True

def test_elementalist_in_sandstorm():
    mode = GameMode()
    world = MagicMock()
    world.arena.weather = "sandstorm"
    world.arena.name = "basic"

    ball = MockBall()
    mode.apply_dynamic_traits(world, [ball], 0.1)

    assert abs(ball.speed - 115.0) < 0.01
    assert abs(ball.defense_multiplier - 0.7) < 0.01
