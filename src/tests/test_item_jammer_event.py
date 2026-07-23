import sys
import os
import pytest
from unittest.mock import MagicMock

sys.path.append(os.path.abspath('src'))
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id=1, alive=True, ball_type="normal"):
        self.id = id
        self.alive = alive
        self.ball_type = ball_type
        self.emp_disabled_timer = 0.0
        self.silence_timer = 0.0
        self.hp = 100.0

def test_item_jammer_event_mode():
    mode = GAME_MODES.get('item_jammer_event')
    assert mode is not None, "ItemJammerEventMode not registered."

    world = MagicMock()
    # explicitly remove leaderboard_manager and profile_manager to fallback correctly
    del world.leaderboard_manager
    del world.profile_manager
    world.add_event = MagicMock()

    ball1 = MockBall(1)
    ball2 = MockBall(2, alive=False)
    balls = [ball1, ball2]

    mode.setup(world, balls)

    assert mode.jammer_timer == 20.0
    assert not mode.is_jamming

    # Tick down the timer
    mode.tick(world, balls, delta=19.5)
    assert mode.jammer_timer == 0.5
    assert not mode.is_jamming

    mode.tick(world, balls, delta=0.6)
    assert mode.is_jamming
    assert mode.jammer_duration == 10.0
    world.add_event.assert_called_with("item_jammer_start", {"message": "Item Jammer Active! Deployables and boosts disabled."})

    # Tick while jamming
    mode.tick(world, balls, delta=0.1)
    assert ball1.emp_disabled_timer == 0.5
    assert ball1.silence_timer == 0.5
    assert ball2.emp_disabled_timer == 0.0 # dead ball

    # Finish jamming
    mode.tick(world, balls, delta=10.0)
    assert not mode.is_jamming
    assert mode.jammer_timer == 20.0
    world.add_event.assert_called_with("item_jammer_end", {"message": "Item Jammer offline. Systems restored."})
