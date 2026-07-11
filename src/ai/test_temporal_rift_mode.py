import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

def test_temporal_rift_mode_spawns_rifts():
    mode = GAME_MODES["temporal_rifts"]
    world = MockWorld()
    balls = []

    # Fast forward time to trigger rift spawn
    mode.tick(world, balls, delta=6.0)

    # There should be exactly 1 rift
    rifts = [h for h in world.arena.hazards if getattr(h, "kind", "") == "temporal_rift"]
    assert len(rifts) == 1

    rift = rifts[0]
    assert rift.radius == 60.0
    assert rift.damage == 0
    assert 10.0 <= rift.duration <= 20.0

    # Check that time_scale is set properly (either speed up or slow down)
    is_speed_up = 2.0 <= rift.time_scale <= 3.0
    is_slow_down = 0.2 <= rift.time_scale <= 0.5
    assert is_speed_up or is_slow_down

if __name__ == "__main__":
    pytest.main([__file__])
