import pytest
import sys
sys.path.append("src")

from ai.game_modes import TemporalRiftsMode

class DummyArena:
    def __init__(self):
        self.hazards = []
        self.width = 800
        self.height = 600

class DummyWorld:
    def __init__(self):
        self.arena = DummyArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_temporal_rifts_mode_spawn():
    mode = TemporalRiftsMode()
    world = DummyWorld()

    # First tick, 6.0 seconds passed, should trigger spawn
    mode.tick(world, [], delta=6.1)

    # Check if hazards were spawned
    assert len(world.arena.hazards) >= 3
    assert len(world.arena.hazards) <= 5

    # Verify properties
    for h in world.arena.hazards:
        assert getattr(h, "is_temporal_rift", False) == True
        assert h.kind in ["slow_motion_zone", "fast_motion_zone"]
        assert 100 <= h.x <= 700
        assert 100 <= h.y <= 500
        assert 40.0 <= h.radius <= 70.0

    assert len(world.events) == 1
    assert world.events[0][0] == "temporal_rifts_spawned"

def test_temporal_rifts_mode_despawn_old():
    mode = TemporalRiftsMode()
    world = DummyWorld()

    # First tick
    mode.tick(world, [], delta=6.1)
    first_batch_hazards = list(world.arena.hazards)
    assert len(first_batch_hazards) >= 3

    # Second tick, another 6.1s passed
    mode.tick(world, [], delta=6.1)

    # The new hazards should have replaced the old ones
    # (Since we just append, the actual hazard objects will be different)
    current_hazards = world.arena.hazards
    assert len(current_hazards) >= 3

    for h in first_batch_hazards:
        assert h not in current_hazards
