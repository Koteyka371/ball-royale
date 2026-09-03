import pytest
from ai.game_modes import OrbitingSpotlightMode
from arena.procedural_arena import ProceduralArena

class MockWorld:
    def __init__(self):
        self.arena = ProceduralArena(2000.0)
        self.events = []

def test_orbiting_spotlight_mode():
    world = MockWorld()
    mode = OrbitingSpotlightMode()
    balls = []

    mode.setup(world, balls)
    assert mode.initial_radius == world.arena.safe_zone_radius
    assert mode.orbit_angle == 0.0

    # Tick to update safe zone center
    mode.tick(world, balls, 0.1)

    import math
    cx = world.arena.width / 2.0
    cy = world.arena.height / 2.0
    orbit_radius = world.arena.width * 0.3

    expected_x = cx + math.cos(mode.orbit_angle) * orbit_radius
    expected_y = cy + math.sin(mode.orbit_angle) * orbit_radius

    assert world.arena.safe_zone_center == (expected_x, expected_y)

    initial_angle = mode.orbit_angle

    # Shrink the safe zone
    world.arena.safe_zone_radius *= 0.5

    mode.tick(world, balls, 0.1)

    assert mode.orbit_angle > initial_angle

    # Fast rotation at end
    world.arena.safe_zone_radius = 0.0
    angle_before = mode.orbit_angle
    mode.tick(world, balls, 0.1)

    speed_at_end = (mode.orbit_angle - angle_before) / 0.1
    assert speed_at_end == pytest.approx(3.0)
