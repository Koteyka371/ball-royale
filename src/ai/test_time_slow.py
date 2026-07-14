import pytest
from unittest.mock import MagicMock
from ai.game_modes import GAME_MODES, TimeDilationZoneMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append({"type": event_type, "data": data})

class MockBall:
    def __init__(self, x, y, vx, vy):
        self.alive = True
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.slow_timer = 1.0

def test_time_dilation_zone_mode():
    mode = GAME_MODES['time_dilation_zone']
    world = MockWorld()

    b1_in_zone = MockBall(500, 500, 100, 0)
    b2_out_of_zone = MockBall(100, 100, 100, 0)

    balls = [b1_in_zone, b2_out_of_zone]

    mode.setup(world, balls)

    assert mode.zone_x == 500.0
    assert mode.zone_y == 500.0

    # Tick with delta 0.1
    mode.tick(world, balls, 0.1)

    # b1 in zone should have its movement reverted by 50%
    # b1.x -= 100 * 0.1 * 0.5 -> b1.x -= 5
    assert b1_in_zone.x == 495.0

    # b1 timer should have 0.1 * 0.5 added to it
    assert b1_in_zone.slow_timer == 1.05

    # b2 out of zone should be unaffected
    assert b2_out_of_zone.x == 100.0
    assert b2_out_of_zone.slow_timer == 1.0

    # Check visual effect event
    assert len(world.events) > 0
    assert world.events[-1]["type"] == "visual_effect"
    assert world.events[-1]["data"]["type"] == "time_dilation_zone"

    # Test hazard slowing
    hazard = MagicMock()
    hazard.active = True
    hazard.x = 500.0
    hazard.y = 500.0
    hazard.vx = 200.0
    hazard.vy = 0.0
    hazard.duration = 2.0

    world.arena.hazards = [hazard]

    mode.tick(world, balls, 0.1)

    # 500 - (200 * 0.1 * 0.5) = 490
    assert hazard.x == 490.0
    # 2.0 + (0.1 * 0.5) = 2.05
    assert hazard.duration == 2.05
