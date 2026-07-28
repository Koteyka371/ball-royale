import pytest
from unittest.mock import MagicMock
from ai.game_modes import HazardShiftEventMode

def test_hazard_shift_event_mode():
    mode = HazardShiftEventMode()
    assert mode.name == "Hazard Shift Event"
    assert mode.is_active is False
    assert mode.event_timer == 15.0

    class MockArena:
        def __init__(self):
            self.hazards = [
                {"x": 100, "y": 100},
                MagicMock(x=500, y=500)
            ]
            self.width = 1000
            self.height = 1000

    class MockWorld:
        def __init__(self):
            self.arena = MockArena()
            self.events = []

        def add_event(self, event_type, data):
            self.events.append((event_type, data))

    world = MockWorld()

    # Tick down to trigger
    balls = [MagicMock(vx=10.0, vy=10.0, alive=True)]

    # Tick 14.99 seconds
    mode.apply_dynamic_traits(world, balls, delta=14.99)
    assert not mode.is_active
    assert not world.events

    # Tick the last bit to trigger the event
    mode.apply_dynamic_traits(world, balls, delta=0.02)
    assert mode.is_active
    assert len(world.events) == 1
    assert world.events[0][0] == "hazard_shift_start"

    # Check that hazards moved
    assert world.arena.hazards[0]["x"] != 100 or world.arena.hazards[0]["y"] != 100
    assert world.arena.hazards[1].x != 500 or world.arena.hazards[1].y != 500

    # Tick while active to verify velocity impulses
    original_vx = balls[0].vx
    original_vy = balls[0].vy
    mode.apply_dynamic_traits(world, balls, delta=0.1)

    # Velocity should have changed due to impulse
    assert balls[0].vx != original_vx or balls[0].vy != original_vy

    # Test ending the event
    mode.apply_dynamic_traits(world, balls, delta=3.0)
    assert not mode.is_active
    assert mode.event_timer == 15.0
