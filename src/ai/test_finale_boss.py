import math
from unittest.mock import MagicMock
from ai.game_modes import BattleRoyaleMode
from arena.procedural_arena import ProceduralArena, Hazard

def test_battle_royale_finale_boss():
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

    # Tick for 119 seconds, boss shouldn't spawn
    mode.tick(world, [b1], delta=119.0)
    assert not any(getattr(h, "kind", "") == "finale_boss" for h in world.arena.hazards)

    # Tick for 2 seconds, boss should spawn
    mode.tick(world, [b1], delta=2.0)

    bosses = [h for h in world.arena.hazards if getattr(h, "kind", "") == "finale_boss"]
    assert len(bosses) == 1
    boss = bosses[0]

    assert boss.radius == 50.0

    # Tick again to see radius expand and damage applied
    mode.tick(world, [b1], delta=1.0)
    assert boss.radius == 55.0

    # Check if projectile spawned
    projectiles = [h for h in world.arena.hazards if getattr(h, "kind", "") == "boss_projectile"]
    assert len(projectiles) >= 1
