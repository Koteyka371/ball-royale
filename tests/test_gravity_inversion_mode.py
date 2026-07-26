import pytest
from ai.game_modes import GAME_MODES

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.active = True
        self.ball_type = "player"

def test_gravity_inversion_mode():
    mode = GAME_MODES["gravity_inversion"]
    world = MockWorld()
    ball1 = MockBall("b1", 10.0, 10.0)
    balls = [ball1]

    mode.setup(world, balls)
    mode.inversion_timer = 0.1

    mode.tick(world, balls, 0.15)

    assert mode.inversion_duration > 0
    assert len(world.events) > 0
    assert world.events[0][0] == "gravity_inversion"

    initial_vx = ball1.vx
    initial_vy = ball1.vy

    mode.tick(world, balls, 0.1)

    assert ball1.vx != initial_vx
    assert ball1.vy != initial_vy
