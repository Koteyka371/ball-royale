import pytest
from ai.game_modes import ToxicMicroSafeZoneMode
from unittest.mock import MagicMock

class MockWorld:
    def __init__(self):
        self.arena = MagicMock()
        self.arena.width = 1000
        self.arena.height = 1000
        self.events = []

    def add_event(self, type, data):
        self.events.append((type, data))

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 100.0
        self.alive = True
        self.ball_type = "player"
        self.poison_timer = 0.0

def test_toxic_micro_safe_zone_trigger_and_damage():
    mode = ToxicMicroSafeZoneMode()
    world = MockWorld()

    b1 = MockBall(500, 500) # Center

    mode.setup(world, [b1])

    # Force late game threshold
    mode.zone_radius = mode.late_game_threshold - 10

    # Tick to trigger
    mode.tick(world, [b1], 1.0)

    assert mode.toxic_phase_active
    assert mode.shrink_rate == 0.0

    # Tick to spawn a micro zone
    mode.micro_zone_spawn_timer = -1.0
    mode.tick(world, [b1], 1.0)

    assert len(mode.micro_zones) == 1
    mz = mode.micro_zones[0]

    # Test taking toxic damage when NOT in micro zone, but in main zone
    # We move b1 to be right in the center of the main zone, but we ensure the micro zone is NOT on top of it.
    b1.x = 500
    b1.y = 500
    mode.zone_x = 500
    mode.zone_y = 500

    # Move the micro zone away from b1
    mz["x"] = 400
    mz["y"] = 400
    mz["radius"] = 50

    initial_hp = b1.hp
    mode.tick(world, [b1], 1.0)

    assert b1.hp < initial_hp
    assert b1.poison_timer >= 3.0

    # Now put b1 INSIDE the micro zone
    b1.x = 400
    b1.y = 400
    b1.hp = 100.0

    mode.tick(world, [b1], 1.0)

    assert b1.hp == 100.0 # No damage taken
