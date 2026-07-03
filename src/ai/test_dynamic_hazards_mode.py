import math
from unittest.mock import MagicMock
from ai.game_modes import DynamicHazardsMode

def test_dynamic_hazards_mode_basic():
    mode = DynamicHazardsMode()
    world = MagicMock()
    # Ensure leaderboard_manager is NOT present to use default season logic,
    # OR set it to return a proper int so GameMode.setup doesn't crash on MagicMock key
    del world.leaderboard_manager
    del world.profile_manager
    world.arena = MagicMock()
    world.arena.hazards = []
    world.arena.width = 1000.0
    world.arena.height = 1000.0
    world.current_tick = 0

    balls = [MagicMock(), MagicMock()]
    for b in balls:
        b.hp = 100
        b.alive = True

    mode.setup(world, balls)

    # Tick past 3.0 seconds to spawn a hazard
    mode.spawn_timer = 2.9
    mode.tick(world, balls, delta=0.2)

    assert len(world.arena.hazards) > 0, "Hazard should have spawned"
    hazard = world.arena.hazards[0]
    assert hasattr(hazard, 'vx') and hasattr(hazard, 'vy')

    old_x = hazard.x
    old_y = hazard.y
    mode.tick(world, balls, delta=0.2)
    assert hazard.x != old_x or hazard.y != old_y, "Hazard should move"
