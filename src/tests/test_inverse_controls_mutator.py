import pytest
from unittest.mock import MagicMock
from ai.game_modes import GAME_MODES

def test_inverse_controls_mutator_setup_and_tick():
    mutator = GAME_MODES.get("inverse_controls_mutator")
    assert mutator is not None

    world = MagicMock()
    # explicitly clear attributes to prevent base class setup from failing on MagicMock objects
    del world.leaderboard_manager
    del world.profile_manager
    del world.arena

    # Explicitly set all boolean flags to prevent MagicMock evaluating to True
    b1 = MagicMock(alive=True, ball_type="player", invert_timer=0.0)
    # delete weather_immunity_timer to avoid NameError delta
    del b1.weather_immunity_timer

    b2 = MagicMock(alive=False, ball_type="player", invert_timer=0.0)
    del b2.weather_immunity_timer

    b3 = MagicMock(alive=True, ball_type="spectator", invert_timer=0.0)
    del b3.weather_immunity_timer

    balls = [b1, b2, b3]

    mutator.setup(world, balls)

    # Initial state should be cooldown
    mutator.timer = 0.0
    mutator.currently_inverted = False

    mutator.tick(world, balls, delta=0.016)

    # Should become inverted
    assert mutator.currently_inverted == True
    assert mutator.timer == 3.0
    assert "inverse_controls" in mutator.mutators

    # Only b1 should get the timer
    assert b1.invert_timer == 3.0
    assert b2.invert_timer == 0.0
    assert b3.invert_timer == 0.0

    # Wait for duration
    mutator.timer = 0.0
    mutator.tick(world, balls, delta=0.016)

    # Should go on cooldown
    assert mutator.currently_inverted == False
    assert mutator.timer == 15.0
    assert "inverse_controls" not in mutator.mutators
