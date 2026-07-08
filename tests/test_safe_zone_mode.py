import pytest
from ai.game_modes import SafeZoneMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []
        self.events = []

    def add_event(self, type_name, data):
        self.events.append((type_name, data))

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.ball_type = "test"
        self.hp = 100
        self.team = "test"

def test_safe_zone_mode_movement():
    world = MockWorld()
    mode = SafeZoneMode()
    balls = []

    mode.setup(world, balls)

    # Verify initial target matches initial position
    assert mode.zone_x == 500.0
    assert mode.zone_y == 500.0
    assert mode.zone_target_x == 500.0
    assert mode.zone_target_y == 500.0

    # Change target and tick
    mode.zone_target_x = 600.0
    mode.zone_target_y = 500.0

    mode.tick(world, balls, delta=1.0)

    # Should have moved towards target
    assert mode.zone_x > 500.0
    assert mode.zone_y == 500.0

    # If it reaches target, it should pick a new one
    mode.zone_x = 596.0
    mode.tick(world, balls, delta=1.0)
    assert mode.zone_target_x != 600.0 or mode.zone_target_y != 500.0

def test_camping_shrink():
    world = MockWorld()
    mode = SafeZoneMode()
    balls = [MockBall(500, 500), MockBall(500, 500)]

    mode.setup(world, balls)
    mode.shrink_rate = 10.0
    initial_radius = mode.zone_radius

    mode.tick(world, balls, delta=1.0)

    # 2 players in zone: multiplier = 2.0 => shrink_rate = 20.0
    assert mode.zone_radius == initial_radius - 20.0
