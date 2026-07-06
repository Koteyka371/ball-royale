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

    # Outward gravity should push it to the right (x > 600)
    assert b1.x > 600.0
    b1_x_outward = b1.x

    # Trigger event
    mode.event_active = True
    mode.event_duration = 5.0

    # Tick with event
    mode.tick(world, [b1], delta=1.0)

    # Inward gravity should pull it left (x < b1_x_outward)
    assert b1.x < b1_x_outward

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
