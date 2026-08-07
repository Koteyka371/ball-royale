import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from ai.game_modes import GAME_MODES
from unittest.mock import MagicMock

def test_confetti_celebration_mode():
    mode = GAME_MODES["confetti_celebration"]

    dead_ball = MagicMock()
    dead_ball.x = 100.0
    dead_ball.y = 100.0
    dead_ball.alive = False

    b1 = MagicMock()
    b1.x = 150.0
    b1.y = 150.0
    b1.alive = True
    b1.ball_type = "normal"
    b1.is_blinded = False
    b1.blindness_timer = 0.0
    b1.speed_boost_timer = 0.0

    b2 = MagicMock()
    b2.x = 1000.0
    b2.y = 1000.0
    b2.alive = True
    b2.ball_type = "normal"
    b2.is_blinded = False
    b2.blindness_timer = 0.0
    b2.speed_boost_timer = 0.0

    world = MagicMock()
    world.balls = [dead_ball, b1, b2]

    mode.on_ball_died(world, dead_ball, killer=None)

    assert getattr(b1, "is_blinded", False) == True
    assert getattr(b1, "blindness_timer", 0.0) == 2.0
    assert getattr(b1, "speed_boost_timer", 0.0) == 3.0

    assert getattr(b2, "is_blinded", False) == False
    assert getattr(b2, "blindness_timer", 0.0) == 0.0
    assert getattr(b2, "speed_boost_timer", 0.0) == 0.0
