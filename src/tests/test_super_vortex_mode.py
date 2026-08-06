import pytest
from unittest.mock import Mock
from ai.game_modes import SuperVortexMode

def test_super_vortex_mode_phases():
    mode = SuperVortexMode()
    world = Mock()
    world.leaderboard_manager = Mock()
    world.leaderboard_manager.data = {'current_season': 1}
    world.profile_manager = Mock()
    world.profile_manager.leaderboard_manager = Mock()
    world.profile_manager.leaderboard_manager.data = {'current_season': 1}
    world.dead_balls = []
    world.arena = Mock()
    world.arena.width = 1000.0
    world.arena.height = 1000.0

    b = Mock()
    b.x = 200.0
    b.y = 200.0
    b.vx = 0.0
    b.vy = 0.0
    b.alive = True
    b.ball_type = "player"
    b.traits = []
    b.badges = []
    b.active_perks = []
    b.mutators = []
    b.base_speed = 100.0
    b.speed = 100.0
    b.base_damage = 10.0
    b.damage = 10.0
    b.max_hp = 100.0
    b.hp = 100.0
    b.lifesteal = 0.0
    b.cooldown_multiplier = 1.0
    b.experience = 0.0
    b.level = 1

    # Setup mode
    mode.setup(world, [b])

    assert mode.phase == "split"
    assert len(mode.bhs) == 3

    # Fast forward to just before merge
    mode.phase_timer = 0.1
    mode.tick(world, [b], 0.1)

    assert mode.phase == "merged"
    assert mode.phase_timer == mode.merged_duration

    # Save velocity during split pull
    split_vx = b.vx
    split_vy = b.vy

    # Test merge pull
    mode.tick(world, [b], 1.0)

    assert b.vx > split_vx or b.vy > split_vy, "Pull should be significantly stronger in merged phase."

def test_super_vortex_mode_tick():
    mode = SuperVortexMode()
    world = Mock()
    world.leaderboard_manager = Mock()
    world.leaderboard_manager.data = {'current_season': 1}
    world.profile_manager = Mock()
    world.profile_manager.leaderboard_manager = Mock()
    world.profile_manager.leaderboard_manager.data = {'current_season': 1}
    world.dead_balls = []
    world.arena = Mock()
    world.arena.width = 1000.0
    world.arena.height = 1000.0

    b = Mock()
    b.x = 0.0
    b.y = 0.0
    b.vx = 0.0
    b.vy = 0.0
    b.alive = True
    b.ball_type = "player"
    b.traits = []
    b.badges = []
    b.active_perks = []
    b.mutators = []
    b.base_speed = 100.0
    b.speed = 100.0
    b.base_damage = 10.0
    b.damage = 10.0
    b.max_hp = 100.0
    b.hp = 100.0
    b.lifesteal = 0.0
    b.cooldown_multiplier = 1.0
    b.experience = 0.0
    b.level = 1

    mode.setup(world, [b])

    mode.tick(world, [b], 1.0)

    # Test boundary bounces
    assert mode.bhs[0]["x"] > 0
