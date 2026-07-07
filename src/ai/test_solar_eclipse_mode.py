import pytest
from ai.game_modes import SolarEclipseEventMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []
        self.is_eclipse = False
        self.is_lunar_eclipse = False
        self.is_night = False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.boosters = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self):
        self.x = 500
        self.y = 500
        self.radius = 15
        self.perception_radius = 250.0
        self.base_perception_radius = 250.0
        self.alive = True
        self.ball_type = "tank"
        self.hp = 50.0
        self.max_hp = 100.0
        self.has_night_vision = False

def test_solar_eclipse_setup():
    mode = SolarEclipseEventMode()
    world = MockWorld()
    b1 = MockBall()
    b2 = MockBall()
    b3 = MockBall()

    # We monkey patch random to ensure we get some night vision
    import random
    orig_random = random.random
    try:
        def mock_random():
            if not hasattr(mock_random, "count"):
                mock_random.count = 0
            mock_random.count += 1
            if mock_random.count == 1:
                return 0.1 # < 0.3 -> night vision
            return 0.9 # > 0.3 -> no night vision
        random.random = mock_random
        mode.setup(world, [b1, b2, b3])
    finally:
        random.random = orig_random

    assert b1.has_night_vision == True
    assert b2.has_night_vision == False
    assert len(world.arena.hazards) == 5
    assert all(h.kind == "solar_panel" for h in world.arena.hazards)

def test_solar_eclipse_tick_logic():
    mode = SolarEclipseEventMode()
    world = MockWorld()
    b = MockBall()
    b.has_night_vision = False

    # Needs a solar panel on top of the ball
    class TempHazard:
        def __init__(self):
            self.kind = "solar_panel"
            self.x = 500
            self.y = 500
            self.radius = 30
            self.hp = 100.0

    world.arena.hazards = [TempHazard()]

    # Force eclipse
    mode.event_active = True
    mode.event_duration = 20.0
    mode.darkness_level = 0.0

    # Tick once, eclipse starts, should heal because darkness < 0.5
    b.hp = 50.0
    mode.tick(world, [b], 0.1)
    assert b.hp > 50.0 # 50.0 + 5.0 * 0.1

    # Fast forward to high darkness (darkness > 0.5)
    mode.event_duration = 10.0
    mode.darkness_level = 0.9

    b.hp = 50.0
    mode.tick(world, [b], 0.1)
    assert b.hp == 50.0 # No healing because darkness > 0.5
    assert b.perception_radius < 250.0 # Perception reduced

    # Check night vision
    b2 = MockBall()
    b2.has_night_vision = True
    mode.tick(world, [b2], 0.1)
    assert b2.perception_radius == 250.0 # Unaffected

    # Check shadow booster spawn (darkness > 0.8)
    mode.spawn_timer = 2.0
    mode.tick(world, [b], 0.1)
    assert len(world.boosters) > 0
    assert world.boosters[0].kind == "shadow_booster"
