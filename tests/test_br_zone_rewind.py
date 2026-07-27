import sys
import pytest
sys.path.append('src')
from ai.game_modes import BattleRoyaleMode

class MockWorld:
    def __init__(self):
        self.dead_balls = []

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockBall:
    def __init__(self, id, btype):
        self.id = id
        self.ball_type = btype
        self.alive = True
        self.team = btype
        self.x = 0.0
        self.y = 0.0
        self.hp = 10.0

def test_battle_royale_zone_rewind():
    mode = BattleRoyaleMode()
    world = MockWorld()
    world.arena = MockArena()
    balls = [MockBall(1, "warrior")]

    # Tick inside the zone to record history
    balls[0].x = 500.0
    balls[0].y = 500.0
    mode.setup(world, balls)
    mode.zone_x = 500.0
    mode.zone_y = 500.0
    mode.zone_radius = 200.0
    # Clear wind to not displace it
    mode.wind_dx = 0
    mode.wind_dy = 0
    mode.weather = "clear"

    mode.tick(world, balls, delta=1.0)

    # Tick outside the zone to trigger rewind
    balls[0].x = 10000.0  # Far outside zone
    balls[0].y = 10000.0
    mode.tick(world, balls, delta=1.0)

    assert balls[0].hp == 10.0
    assert balls[0].alive
    # Should be rewound to the position it had before (with a small tolerance if physics moves it)
    assert abs(balls[0].x - 500.0) < 10.0
    assert abs(balls[0].y - 500.0) < 10.0
