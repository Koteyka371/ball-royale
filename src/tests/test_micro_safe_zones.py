import pytest
import math
from unittest.mock import MagicMock
from ai.game_modes import MicroSafeZonesMode

class MockEntity:
    def __init__(self, id, x, y, hp=100.0, team="team1"):
        self.id = id
        self.x = x
        self.y = y
        self.hp = hp
        self.team = team
        self.alive = True
        self.ball_type = "normal"
        self.poison_timer = 0.0

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []

def test_micro_safe_zones_mode():
    mode = MicroSafeZonesMode()
    world = MockWorld()

    # Create two balls, one inside a micro zone, one outside
    # Let's set it up so we know where micro zones are
    b1 = MockEntity(1, 500, 500) # Should be in center micro zone
    b2 = MockEntity(2, 550, 550) # Should be outside micro zone

    balls = [b1, b2]

    mode.setup(world, balls)

    # Force late game condition
    mode.zone_radius = 200.0
    mode.zone_x = 500.0
    mode.zone_y = 500.0

    # Tick to spawn a micro zone
    # We will manually set the micro zone to ensure testing correctness
    mode.tick(world, balls, delta=0.1)

    # Overwrite the random micro zone with a known one
    mode.micro_zones = [{"x": 500.0, "y": 500.0, "radius": 20.0, "duration": 8.0}]

    b1_initial_hp = b1.hp
    b2_initial_hp = b2.hp

    # Tick again to apply damage
    mode.tick(world, balls, delta=1.0)

    # b1 is at 500, 500 (distance 0 from micro zone center) -> inside micro zone -> should not take toxic gas damage
    # b1 might take outside damage if it was outside the primary safe zone, but it's at 500,500 which is primary safe zone center.
    # Actually SafeZoneMode base class applies damage outside zone_radius.
    # b1 is at distance 0 from primary zone center, primary radius is 200, so b1 doesn't take primary damage either.
    # Wait, b2 is at 550, 550, distance from 500, 500 is sqrt(50^2 + 50^2) = 70.7.
    # This is inside primary zone radius (200), but outside micro zone radius (20).
    # So b2 should take toxic gas damage!

    # Let's check b1: no damage
    assert math.isclose(b1.hp, b1_initial_hp), f"b1 should not take damage, got hp {b1.hp} from {b1_initial_hp}"

    # Let's check b2: took toxic gas damage (25.0 * 1.0 = 25.0)
    assert b2.hp < b2_initial_hp, f"b2 should take damage, got hp {b2.hp}"
    assert b2.hp <= b2_initial_hp - 20.0, "b2 should take significant gas damage"
