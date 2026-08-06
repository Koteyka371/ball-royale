import pytest
from unittest.mock import Mock

def test_floor_paint_mode():
    from ai.game_modes import FloorPaintMode

    mode = FloorPaintMode()
    world = Mock()
    world.attacks = []
    world.dead_balls = []

    # Avoid mock iterability issues
    del world.leaderboard_manager
    del world.profile_manager
    world.arena = None
    world.weekly_mutator = ""
    world.mutators_active = False
    world.mutators = []
    world.boosters = []

    b1 = Mock()
    b1.hologram_clones = []
    b1.hologram_clones = []
    b1.x, b1.y = 100.0, 100.0
    b1.team = "Red"
    b1.alive = True
    b1.radius = 20.0
    b1.base_speed = 100.0
    b1.speed = 100.0
    b1.damage = 10.0
    b1.base_damage = 10.0
    b1.hp = 100.0
    b1.max_hp = 100.0
    b1._paint_cd = 10.0 # prevent auto-splatting for test control
    b1.traits = []
    b1.sponsor = None
    b1.is_quantum_entangled = False
    b1.ball_type = "test_ball"

    b2 = Mock()
    b2.hologram_clones = []
    b2.hologram_clones = []
    b2.x, b2.y = 300.0, 300.0
    b2.team = "Blue"
    b2.alive = True
    b2.radius = 20.0
    b2.base_speed = 100.0
    b2.speed = 100.0
    b2.damage = 10.0
    b2.base_damage = 10.0
    b2.hp = 100.0
    b2.max_hp = 100.0
    b2._paint_cd = 10.0
    b2.traits = []
    b2.sponsor = None
    b2.is_quantum_entangled = False
    b2.ball_type = "test_ball"

    balls = [b1, b2]

    # Setup can have deep mocking requirements that change. We can just append the splats and call tick.
    # Actually, we don't even need to call setup for our test, because our logic doesn't depend on it.
    mode.splats.append(mode.Splat(100.0, 100.0, "Red", radius=50.0))
    mode.splats.append(mode.Splat(300.0, 300.0, "Red", radius=50.0))

    mode.tick(world, balls, 0.1)

    # b1 is on Red paint (ally). Speed should be boosted.
    assert b1.speed == 150.0
    # b2 is on Red paint (enemy). Speed should be reduced.
    assert b2.speed == 50.0
