import pytest
from unittest.mock import MagicMock
from ai.game_modes import GameMode, GAME_MODES
import math

def test_phantom_replay_hazard_logic():
    from ai.game_modes import PhantomReplayHazardMode
    mode = PhantomReplayHazardMode()
    world = MagicMock()
    world.leaderboard_manager.data.get.return_value = 1

    b1 = MagicMock()
    b1.is_submerged = False
    b1.submerge_timer = 0.0
    b1.wet_debuff_timer = 0.0
    b1.id = 1
    b1.alive = True
    b1.x, b1.y = 500, 500
    b1.radius = 10

    b2 = MagicMock()
    b2.is_submerged = False
    b2.submerge_timer = 0.0
    b2.wet_debuff_timer = 0.0
    b2.id = 2
    b2.alive = True
    b2.x, b2.y = 100, 100
    b2.radius = 10

    balls = [b1, b2]
    mode.setup(world, balls)

    # Record phase: 3s
    # Tick 1s
    mode.tick(world, balls, 1.0)
    assert 1 in mode.recordings
    assert 2 not in mode.recordings

    # Tick 2s
    b1.x, b1.y = 550, 500
    mode.tick(world, balls, 2.0)

    assert mode.phase == "delay"
    assert mode.timer == 0.0

    # Delay phase: 1s
    mode.tick(world, balls, 1.0)
    assert mode.phase == "replay"
    assert len(mode.phantoms) == 1

    p = mode.phantoms[0]
    assert p.target_id == 1
    assert p.x == 500

    # Replay phase: 3s
    b1.take_damage.reset_mock()
    mode.tick(world, balls, 1.5)
    assert p.x > 500

    b1.x, b1.y = p.x, p.y
    mode.tick(world, balls, 0.1)
    b1.take_damage.assert_called()
