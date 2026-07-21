from unittest.mock import MagicMock
from ai.game_modes import RisingLavaMode
from arena.procedural_arena import Platform

def test_rising_lava_mode():
    mode = RisingLavaMode()
    world = MagicMock()
    world.arena = MagicMock()
    world.arena.height = 1000.0
    world.arena.platforms = [
        Platform(100, 950, 100, 20, 0, 0),
        Platform(100, 500, 100, 20, 0, 0)
    ]

    ball1 = MagicMock(alive=True, y=960.0, hp=100.0)
    ball2 = MagicMock(alive=True, y=400.0, hp=100.0)

    # Tick 1: Initialize
    mode.apply_dynamic_traits(world, [ball1, ball2], 1.0)
    assert mode.lava_y == 1000.0 - 10.0

    # Tick a lot to submerge ball1 and platform 1
    mode.apply_dynamic_traits(world, [ball1, ball2], 4.0)
    # lava_y is now 950.0. platform 1 is at 950. ball 1 is at 960 (submerged)

    assert len(world.arena.platforms) == 1
    assert world.arena.platforms[0].y == 500

    assert ball1.hp == 0.0  # 100 - 50*4.0 = -100 -> 0.0
    assert ball2.hp == 100.0 # not submerged
