import pytest
from ai.game_modes import SolarFlareEventMode

class MockArena:
    def __init__(self):
        self.is_night = False
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, name, data):
        self.events.append(data)

class MockBall:
    def __init__(self, b_type="warrior"):
        self.id = 1
        self.ball_type = b_type
        self.x = 500.0
        self.y = 500.0
        self.alive = True
        self.radius = 15.0
        self.hp = 100.0

def test_solar_flare_event_trigger():
    mode = SolarFlareEventMode()
    world = MockWorld()
    b1 = MockBall("warrior")

    mode.event_timer = 31.0
    import random
    original_random = random.random
    try:
        random.random = lambda: 0.1 # Force < 0.2
        mode.tick(world, [b1], delta=0.2)
    finally:
        random.random = original_random

    assert mode.event_active
    assert world.events[0]["message"] == "A SOLAR FLARE HAS BEGUN!"

def test_solar_flare_effects():
    mode = SolarFlareEventMode()
    world = MockWorld()
    b1 = MockBall("warrior")

    mode.event_active = True
    mode.event_duration = 5.0

    # Tick once
    mode.tick(world, [b1], delta=1.0)

    # Check arena shrunk
    assert world.arena.width == 980.0
    assert world.arena.height == 980.0

    # Check damage taken (5 dps)
    assert b1.hp == 95.0

    # Ensure ball is pushed inwards if it was outside bounds
    b1.x = 1000.0
    b1.y = 1000.0

    mode.tick(world, [b1], delta=1.0)

    assert world.arena.width == 960.0
    assert world.arena.height == 960.0

    assert b1.x <= 960.0 - 15.0
    assert b1.y <= 960.0 - 15.0

    assert b1.hp == 90.0

def test_solar_flare_end():
    mode = SolarFlareEventMode()
    world = MockWorld()
    b1 = MockBall("warrior")

    mode.event_active = True
    mode.event_duration = 1.0

    mode.tick(world, [b1], delta=2.0)

    assert not mode.event_active
    assert world.events[-1]["message"] == "The Solar Flare has ended."
