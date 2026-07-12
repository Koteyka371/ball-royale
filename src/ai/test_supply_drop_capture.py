import pytest
from unittest.mock import MagicMock
from ai.game_modes import SupplyDropCaptureMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, type, data):
        self.events.append((type, data))

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.hp = 50.0
        self.max_hp = 100.0
        self.base_speed = 100.0
        self.speed = 100.0
        self.base_damage = 10.0
        self.damage = 10.0

def test_supply_drop_capture_mode():
    mode = SupplyDropCaptureMode()
    world = MockWorld()
    b1 = MockBall(500, 500)
    balls = [b1]

    # Spawn drop by ticking 20 seconds
    mode.tick(world, balls, 20.0)

    assert len(mode.supply_drops) == 1
    drop = mode.supply_drops[0]

    # Move ball to drop
    b1.x = drop.x
    b1.y = drop.y

    # Tick capture progress (5.0 seconds needed)
    mode.tick(world, balls, 2.5)
    assert drop.capture_progress > 0
    assert len(mode.supply_drops) == 1
    assert b1.hp == 50.0  # Not healed yet

    mode.tick(world, balls, 3.0)

    # Should be captured
    assert len(mode.supply_drops) == 0
    assert b1.hp == 100.0  # Healed to max_hp
    assert b1.speed == 150.0  # Buffed
    assert b1.damage == 15.0  # Buffed

    # Check events
    event_types = [e[0] for e in world.events]
    assert "supply_drop_spawn" in event_types
    assert "supply_drop_captured" in event_types
