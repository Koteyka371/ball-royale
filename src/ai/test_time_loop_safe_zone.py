import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, x, y):
        self.id = id(self)
        self.x = x
        self.y = y
        self.vx = 10.0
        self.vy = 10.0
        self.alive = True
        self.hp = 100
        self.ball_type = "player"

def test_time_loop_safe_zone_mode():
    mode = GAME_MODES["time_loop_safe_zone"]
    world = MockWorld()

    # Place a ball initially in the center (inside safe zone)
    ball = MockBall(500, 500)

    mode.setup(world, [ball])

    # Tick so the ball's history gets recorded
    mode.tick(world, [ball], delta=0.1)

    assert not ball.is_rewinding
    assert len(ball.time_loop_history) == 1
    assert ball.time_loop_history[0] == (500, 500)

    # Move ball far away (outside safe zone)
    ball.x = 2000
    ball.y = 2000

    # Tick again
    mode.tick(world, [ball], delta=0.1)

    # The ball should be rewound to (500, 500)
    assert ball.is_rewinding
    assert ball.x == 500
    assert ball.y == 500
    assert ball.vx == 0
    assert ball.vy == 0
    assert len(ball.time_loop_history) == 0
