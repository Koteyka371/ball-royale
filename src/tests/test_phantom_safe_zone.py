import pytest
from ai.game_modes import PhantomSafeZoneMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 100.0
        self.alive = True
        self.ball_type = "normal"
        self.slow_timer = 0.0

def test_phantom_safe_zone_initialization():
    mode = PhantomSafeZoneMode()
    assert mode.name == "Phantom Safe Zones"

def test_phantom_safe_zone_tick():
    mode = PhantomSafeZoneMode()
    world = MockWorld()
    b1 = MockBall(100.0, 100.0) # Far from center
    b2 = MockBall(500.0, 500.0) # Center

    balls = [b1, b2]
    mode.setup(world, balls)

    # Ensure zone size is set
    mode.zone_radius = 200.0
    mode.zone_x = 500.0
    mode.zone_y = 500.0

    # Force a phantom zone on top of b1
    mode.phantom_zones = [{
        "x": 100.0,
        "y": 100.0,
        "radius": 50.0,
        "timer": 15.0
    }]

    # Tick
    mode.tick(world, balls, 1.0)

    # B2 is in main zone, should have full hp
    assert b2.hp == 100.0

    # B1 is outside main zone, but inside phantom zone, should have full hp
    # Damage outside is outside_damage_per_second + shrink_ratio * ...
    # Wait, shrink_ratio might differ, but at least b1's hp should be 100.
    # Note: Because of floats, it might be 100.0 or 99.99999999999
    assert b1.hp > 99.0

def test_phantom_safe_zone_dissipates():
    mode = PhantomSafeZoneMode()
    world = MockWorld()
    b1 = MockBall(100.0, 100.0)

    balls = [b1]
    mode.setup(world, balls)

    mode.zone_radius = 200.0
    mode.zone_x = 500.0
    mode.zone_y = 500.0

    mode.phantom_zones = [{
        "x": 100.0,
        "y": 100.0,
        "radius": 50.0,
        "timer": 0.5
    }]

    # Tick past timer
    mode.tick(world, balls, 1.0)

    # Phantom zone should be gone
    assert len(mode.phantom_zones) == 0

    # B1 should have taken damage
    assert b1.hp < 100.0


def test_phantom_safe_zone_prevents_death():
    mode = PhantomSafeZoneMode()
    world = MockWorld()
    b1 = MockBall(100.0, 100.0)
    b1.hp = 5.0 # Low enough that outside storm damage will kill them this tick

    balls = [b1]
    mode.setup(world, balls)
    mode.zone_radius = 200.0
    mode.zone_x = 500.0
    mode.zone_y = 500.0
    mode.outside_damage_per_second = 100.0 # Force lethal damage

    mode.phantom_zones = [{
        "x": 100.0,
        "y": 100.0,
        "radius": 50.0,
        "timer": 15.0
    }]

    # Tick with large delta to ensure lethal damage
    mode.tick(world, balls, 1.0)

    assert b1.alive == True
    assert b1.hp >= 5.0
