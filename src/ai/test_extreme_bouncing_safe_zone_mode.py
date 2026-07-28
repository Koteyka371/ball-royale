import pytest
from ai.game_modes import ExtremeBouncingSafeZoneMode, SafeZoneMode
import math

def test_extreme_bouncing_safe_zone_mode():
    mode = ExtremeBouncingSafeZoneMode()
    assert isinstance(mode, SafeZoneMode)
    assert mode.name == "Extreme Bouncing Safe Zone"
    assert "Extreme Bounciness" in mode.description

def test_extreme_bouncing_safe_zone_mode_multiplier():
    mode = ExtremeBouncingSafeZoneMode()
    # It requires zone_radius to compute bounce_multiplier
    mode.zone_radius = 500.0
    mode.min_zone_radius = 50.0

    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000

    class MockWorld:
        def __init__(self):
            self.arena = MockArena()
            self.width = 1000
            self.height = 1000

    world = MockWorld()
    balls = []

    # Tick should update original radius
    mode.tick(world, balls, 0.016)

    assert mode.bounce_multiplier == pytest.approx(4.0, 0.1)

    mode.zone_radius = 275.0
    mode.tick(world, balls, 0.016)

    # Range is 500 - 50 = 450
    # Current is 275. 275 - 50 = 225
    # Ratio is 225 / 450 = 0.5
    # multiplier = 4.0 + 0.5 * 6.0 = 7.0
    assert mode.bounce_multiplier == pytest.approx(7.0, 0.1)

    mode.zone_radius = 50.0
    mode.tick(world, balls, 0.016)

    # multiplier = 4.0 + 1.0 * 6.0 = 10.0
    assert mode.bounce_multiplier == pytest.approx(10.0, 0.1)
