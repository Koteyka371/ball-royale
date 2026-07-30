import pytest
from ai.game_modes import TimeLoopMode

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, event_data):
        self.events.append({"type": event_type, "data": event_data})

class MockBall:
    def __init__(self, bid, x, y, hp):
        self.id = bid
        self.x = x
        self.y = y
        self.hp = hp
        self.alive = True
        self.inventory = []
        self.vx = 0.0
        self.vy = 0.0

class MockHazard:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def test_time_loop_mode():
    world = MockWorld()

    b1 = MockBall("b1", 10.0, 20.0, 100.0)
    b2 = MockBall("b2", 50.0, 60.0, 100.0)
    balls = [b1, b2]

    h1 = MockHazard(100.0, 100.0)
    world.arena.hazards = [h1]

    mode = TimeLoopMode()
    mode.setup_done = False
    mode.tick(world, balls, 0.0)

    assert mode.saved_state is not None
    assert mode.saved_state["balls"]["b1"]["x"] == 10.0

    # Simulate movement, hp changes and picking up an item
    b1.x = 200.0
    b1.y = 200.0
    b1.hp = 50.0
    b1.inventory.append("gravity_boots")

    h1.x = 300.0
    h1.y = 300.0

    # Tick up to 29.9
    mode.tick(world, balls, 29.9)
    assert b1.x == 200.0
    assert h1.x == 300.0

    # Tick one more time to trigger rewind
    mode.tick(world, balls, 0.2)

    # Assert reset
    assert b1.x == 10.0
    assert b1.y == 20.0
    assert b1.hp == 100.0
    assert h1.x == 100.0
    assert h1.y == 100.0

    # Assert inventory kept
    assert "gravity_boots" in b1.inventory
