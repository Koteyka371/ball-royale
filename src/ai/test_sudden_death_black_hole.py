import math
from unittest.mock import MagicMock
from ai.game_modes import BattleRoyaleMode
from arena.procedural_arena import ProceduralArena, Hazard

def test_battle_royale_sudden_death_black_hole():
    mode = BattleRoyaleMode()
    world = MagicMock()
    del world.leaderboard_manager
    del world.profile_manager
    world.arena = MagicMock()
    world.arena.width = 1000.0
    world.arena.height = 1000.0
    world.arena.hazards = []

    b1 = MagicMock()
    b1.alive = True
    b1.ball_type = "knight"
    b1.x, b1.y = 500.0, 500.0
    b1.hp = 100.0
    b1.weather_control_timer = 0.0
    b1.vision_booster_timer = 0.0

    mode.setup(world, [b1])

    # Tick for 119 seconds, black hole shouldn't spawn
    mode.tick(world, [b1], delta=119.0)
    assert not any(getattr(h, "kind", "") == "massive_black_hole" for h in world.arena.hazards)

    # Tick for 2 seconds, black hole should spawn
    mode.tick(world, [b1], delta=2.0)

    black_holes = [h for h in world.arena.hazards if getattr(h, "kind", "") == "massive_black_hole"]
    assert len(black_holes) == 1
    bh = black_holes[0]

    assert bh.radius == 50.0
    assert bh.lifetime == 0.0
    assert bh.damage == 100.0

    # Tick again to see radius and lifetime expand
    mode.tick(world, [b1], delta=1.0)
    assert bh.radius == 55.0
    assert bh.lifetime == 1.0


    # Tick again to see pull effect
    mode.tick(world, [b1], delta=1.0)

    # Check if ball moved towards black hole (500, 500)
    # The ball is already at 500, 500, so let's move it first to see the pull
    b1.x, b1.y = 100.0, 100.0
    mode.tick(world, [b1], delta=1.0)

    dist_sq = (500.0 - b1.x)**2 + (500.0 - b1.y)**2
    original_dist_sq = (500.0 - 100.0)**2 + (500.0 - 100.0)**2

    assert dist_sq < original_dist_sq
