import pytest
from ai.game_modes import DayNightMode

class MockHazard:
    def __init__(self):
        self.invisible = False

class MockArena:
    def __init__(self):
        self.is_night = False
        self.hazards = [MockHazard()]

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_day_night_eclipse():
    import random
    mode = DayNightMode()
    world = MockWorld()

    mode.setup(world, [])
    mode.phase_duration = 10.0
    mode.timer = 9.9

    original_random = random.random
    try:
        # Force the eclipse to happen
        random.random = lambda: 0.05
        mode.tick(world, [], delta=0.2) # timer becomes 10.1

        assert getattr(mode, "eclipse_timer", 0.0) > 0.0
        assert world.arena.is_lunar_eclipse == True
        assert world.arena.is_eclipse == True

        # Hazard should be invisible
        assert world.arena.hazards[0].invisible == True

        # Fast forward
        mode.eclipse_timer = 0.1
        mode.tick(world, [], delta=0.2) # drops below 0

        assert world.arena.is_lunar_eclipse == False
        assert world.arena.is_eclipse == False
        assert world.arena.hazards[0].invisible == False

    finally:
        random.random = original_random
