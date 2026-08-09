import pytest
from unittest.mock import MagicMock
from ai.game_modes import CenterVortexMode

def test_center_vortex_mode():
    mode = CenterVortexMode()
    world = MagicMock()
    world.arena.width = 1000.0
    world.arena.height = 1000.0
    world.arena.hazards = []
    del world.leaderboard_manager
    del world.profile_manager

    b = MagicMock()
    b.x = 400.0
    b.y = 400.0
    b.vx = 0.0
    b.vy = 0.0
    b.hp = 100.0
    b.alive = True

    p = MagicMock()
    p.x = 400.0
    p.y = 400.0
    p.vx = 0.0
    p.vy = 0.0
    p.hp = 10.0
    p.alive = True

    world.projectiles = [p]

    mode.setup(world, [b])

    # Check that hazard was created
    assert len(world.arena.hazards) == 1
    vx = world.arena.hazards[0]
    assert vx.kind == "vortex"
    assert vx.x == 500.0
    assert vx.y == 500.0

    # Move ball and projectile outside center
    mode.tick(world, [b], 0.1)

    assert b.vx > 0
    assert b.vy > 0
    assert p.vx > 0
    assert p.vy > 0

    # Move close to center to trigger crush
    b.x = 490.0
    b.y = 490.0
    p.x = 490.0
    p.y = 490.0

    hp_before = b.hp
    p_hp_before = p.hp

    mode.tick(world, [b], 0.1)

    # Should take crush damage (-1000)
    assert b.hp <= hp_before - 900
    assert p.hp <= p_hp_before - 900
