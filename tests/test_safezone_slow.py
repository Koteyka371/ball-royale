import pytest
from ai.game_modes import SafeZoneMode

class MockBall:
    def __init__(self, x, y, alive=True, ball_type="normal"):
        self.x = x
        self.y = y
        self.alive = alive
        self.ball_type = ball_type
        self.hp = 100.0
        self.id = "mock_ball"
        self.minimap_ping_timer = 0.0
        self.slow_timer = 0.0

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_name, payload):
        self.events.append((event_name, payload))

def test_safezone_slow_timer():
    world = MockWorld()
    mode = SafeZoneMode()
    balls = [MockBall(0, 0), MockBall(500, 500)]

    mode.setup(world, balls)
    mode.zone_radius = 100.0
    mode.zone_x = 500.0
    mode.zone_y = 500.0

    mode.tick(world, balls, delta=0.1)

    # Ball 0 is outside (dist > 100) -> should have slow_timer updated to 0.5
    assert balls[0].slow_timer >= 0.5
    assert balls[0].hp < 100.0

    # Ball 1 is inside (dist = 0) -> should be unaffected
    assert balls[1].slow_timer == 0.0
    assert balls[1].hp == 100.0
