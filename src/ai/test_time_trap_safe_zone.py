import pytest
from ai.game_modes import GAME_MODES

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
        self.vx = 10.0
        self.vy = 10.0
        self.hp = 100.0
        self.alive = True
        self.ball_type = "player"
        self.team = "player"
        self.id = "test_id_1"

def test_time_trap_safe_zone():
    world = MockWorld()
    mode = GAME_MODES["time_trap_safe_zone"]
    balls = [MockBall(500, 500)]

    mode.setup(world, balls)

    # 1. Stay in safe zone
    balls[0].x = 510
    mode.tick(world, balls, delta=1.0)
    assert len(mode.history["test_id_1"]) == 1

    balls[0].x = 520
    mode.tick(world, balls, delta=1.0)
    assert len(mode.history["test_id_1"]) == 2

    # 2. Go outside safe zone
    balls[0].x = 5000
    mode.tick(world, balls, delta=1.0)

    # Should pop history and revert position/velocity
    assert balls[0].x == 510
    assert balls[0].vx == 0.0
    assert len(mode.history["test_id_1"]) == 0
