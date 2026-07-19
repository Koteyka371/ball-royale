import pytest
from ai.game_modes import PositionSwapMode

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, type_str, data):
        self.events.append((type_str, data))

class MockBall:
    def __init__(self, id_val, team_val):
        self.id = id_val
        self.team = team_val
        self.alive = True
        self.x = float(id_val) * 10
        self.y = float(id_val) * 10

def test_position_swap_mode_trigger():
    mode = PositionSwapMode()
    world = MockWorld()
    b1 = MockBall(1, "A")
    b2 = MockBall(2, "B")
    balls = [b1, b2]

    # Fast forward timer to 0
    mode.apply_dynamic_traits(world, balls, 10.0)

    assert getattr(world, "position_swap_pending", False) is True
    assert getattr(world, "position_swap_telegraph_timer", 0) == mode.telegraph_duration

    telegraph_events = [e for e in world.events if e[0] == "portal_telegraph"]
    assert len(telegraph_events) == 1

    # Tick down the telegraph timer
    mode.apply_dynamic_traits(world, balls, mode.telegraph_duration + 0.1)

    assert getattr(world, "position_swap_pending", False) is False
    assert 3.0 <= getattr(world, "position_swap_timer", 0) <= 8.0

    swap_events = [e for e in world.events if e[0] == "position_swapped"]
    assert len(swap_events) == 1

    # Verify positions swapped
    assert b1.x == 20.0
    assert b1.y == 20.0
    assert b2.x == 10.0
    assert b2.y == 10.0
