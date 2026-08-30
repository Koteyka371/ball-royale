import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id_val, team, x, y):
        self.id = id_val
        self.team = team
        self.x = x
        self.y = y
        self.alive = True
        self.base_speed = 100.0
        self.speed = 100.0
        self.base_damage = 50.0
        self.damage = 50.0

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, event_type, event_data):
        self.events.append({"type": event_type, **event_data})

def test_position_swap_mode():
    mode = GAME_MODES["position_swap"]
    world = MockWorld()

    balls = [
        MockBall(1, "A", 0, 0),
        MockBall(2, "A", 1, 1),
        MockBall(3, "B", 10, 10),
        MockBall(4, "B", 11, 11)
    ]

    # Tick with large delta to trigger swap telegraph
    mode.apply_dynamic_traits(world, balls, 16.0)

    assert getattr(world, "position_swap_pending", False) == True
    telegraph_events = [e for e in world.events if e["type"] == "portal_telegraph"]
    assert len(telegraph_events) > 0
    assert len(getattr(world, "position_swap_pairs", [])) >= 2

    # Tick to finish telegraph
    world.events = []
    mode.apply_dynamic_traits(world, balls, 2.0)

    assert getattr(world, "position_swap_pending", False) == False
    swap_events = [e for e in world.events if e["type"] == "position_swapped"]
    assert len(swap_events) >= 2
