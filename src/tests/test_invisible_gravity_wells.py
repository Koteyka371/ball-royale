import pytest
from unittest.mock import MagicMock
from ai.game_modes import InvisibleGravityWellsMode

def test_invisible_gravity_wells_tick():
    mode = InvisibleGravityWellsMode()
    world = MagicMock()
    world.arena.width = 1000.0
    world.arena.height = 1000.0
    world.leaderboard_manager.data.get.return_value = 1
    world.leaderboard_manager.data.get.return_value = 1

    b1 = MagicMock()
    b1.alive = True
    b1.ball_type = "player"
    b1.x = 500.0
    b1.y = 500.0
    b1.vx = 0.0
    b1.vy = 0.0

    balls = [b1]
    mode.setup(world, balls)

    # Fast forward to trigger well spawn
    mode.spawn_timer = 0.0
    mode.tick(world, balls, 0.1)

    assert len(mode.gravity_wells) == 1
    well = mode.gravity_wells[0]

    # Place player close to the well
    b1.x = well["x"] + 100
    b1.y = well["y"]
    b1.vx = 0.0
    b1.vy = 0.0

    mode.tick(world, balls, 0.1)

    # Should be pulled towards well
    # well.x - b1.x = -100
    # pull is negative in x
    assert b1.vx < 0.0

    # Spectator should not be affected
    b2 = MagicMock()
    b2.alive = True
    b2.ball_type = "spectator"
    b2.x = well["x"] + 100
    b2.y = well["y"]
    b2.vx = 0.0
    b2.vy = 0.0

    balls.append(b2)
    mode.tick(world, balls, 0.1)
    assert b2.vx == 0.0
