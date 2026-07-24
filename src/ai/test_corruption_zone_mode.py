import pytest
from ai.game_modes import CorruptionZoneMode

class MockWorld:
    def __init__(self):
        self.arena = type('MockArena', (), {'width': 1000, 'height': 1000, 'hazards': []})()
        self.balls = []
        self.events = []
        self.leaderboard_manager = type('Mock', (), {'data': {'current_season': 4}})()

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100.0
        self.speed = 100.0
        self.damage = 10.0
        self.base_speed = 100.0
        self.base_damage = 10.0
        self.alive = True

def test_corruption_zone_mode():
    mode = CorruptionZoneMode()
    world = MockWorld()
    ball1 = MockBall(1, 100, 100) # In zone (zone forced to 100, 100)
    ball2 = MockBall(2, 900, 900) # Out of zone
    balls = [ball1, ball2]

    world.balls = balls
    mode.setup(world, balls)

    # Force spawn a zone at 100, 100
    mode.spawn_timer = 0
    mode.tick(world, balls, 1.0)

    assert len(mode.zones) == 1
    mode.zones[0].x = 100
    mode.zones[0].y = 100

    mode.tick(world, balls, 1.0)

    # ball1 should be drained and buffed
    assert ball1.hp == 100.0 - 15.0 # 15.0 drain rate * 1.0 delta
    assert ball1.speed > 100.0
    assert ball1.damage > 10.0
    assert getattr(ball1, "in_corruption_zone", False) == True

    # ball2 should be unaffected
    assert ball2.hp == 100.0
    # speed modified by season/weather
    # damage modified by season/weather
    assert getattr(ball2, "in_corruption_zone", False) == False
