import pytest
from src.ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, type_name, data):
        self.events.append((type_name, data))

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.ball_type = "normal"

def test_reverse_gravity_event_mode():
    mode = GAME_MODES["reverse_gravity_event"]
    world = MockWorld()
    b1 = MockBall(600.0, 500.0)  # to the right of center

    # Tick without event
    mode.tick(world, [b1], delta=1.0)

    # Normal gravity should push it down (y > 500)
    assert b1.y > 500.0
    b1_y_downward = b1.y

    # Trigger event
    mode.event_active = True
    mode.event_duration = 5.0

    # Tick with event
    mode.tick(world, [b1], delta=1.0)

    # Inward gravity should pull it up (y < b1_y_downward)
    assert b1.y < b1_y_downward

def test_reverse_gravity_event_mode_trigger():
    mode = GAME_MODES["reverse_gravity_event"]
    world = MockWorld()
    mode.event_active = False
    mode.event_timer = 21.0

    # Mock random to trigger event
    import random
    original_random = random.random
    random.random = lambda: 0.1

    try:
        mode.tick(world, [], delta=0.1)
        assert mode.event_active == True
        assert mode.event_duration == 9.9
    finally:
        random.random = original_random
