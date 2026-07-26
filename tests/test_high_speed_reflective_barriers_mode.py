import pytest
from ai.game_modes import HighSpeedReflectiveBarriersMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.projectiles = []

class MockEntity:
    def __init__(self, x, y, vx, vy, radius=10.0, alive=True, is_projectile=False):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.alive = alive
        self.is_projectile = is_projectile
        self.hp = 100.0

def test_high_speed_reflective_barriers_mode_setup():
    mode = HighSpeedReflectiveBarriersMode()
    world = MockWorld()

    mode.setup(world, [])

    assert len(world.arena.hazards) == 3
    for hazard in world.arena.hazards:
        assert hazard.kind == "high_speed_reflect_barrier"
        assert hazard.radius == 40.0
        assert 200 <= hazard.x <= 800
        assert 200 <= hazard.y <= 800

def test_high_speed_reflective_barriers_mode_tick():
    mode = HighSpeedReflectiveBarriersMode()
    world = MockWorld()

    # Setup hazard manually
    class DummyHazard:
        def __init__(self):
            self.x = 500.0
            self.y = 500.0
            self.radius = 40.0
            self.kind = "high_speed_reflect_barrier"

    hazard = DummyHazard()
    world.arena.hazards.append(hazard)

    # Entity moving right towards the hazard
    # Hazard is at (500, 500)
    # Entity is at (455, 500), radius 10. Distance = 45. Min dist = 50. Collision!
    ball = MockEntity(455.0, 500.0, 100.0, 0.0)

    mode.apply_dynamic_traits(world, [ball], 0.016)

    # Normal is (-1, 0)
    # Incoming velocity is (100, 0)
    # Dot product: 100 * -1 = -100
    # Reflection: vx = 100 - 2 * (-100) * (-1) = 100 - 200 = -100
    # Speed up: -100 * 1.5 = -150

    assert ball.vx == -150.0
    assert ball.vy == 0.0

    # Check that position was adjusted
    assert ball.x < 455.0

    # Check cooldown
    assert ball.reflect_barrier_cooldown == 0.5

    # Tick again to check cooldown
    mode.apply_dynamic_traits(world, [ball], 0.016)
    assert ball.reflect_barrier_cooldown == 0.5 - 0.016
