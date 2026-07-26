import pytest
from ai.game_modes import RandomDirectionGravityMode

class MockWorld:
    def __init__(self):
        self.events = []
        self.tick_timer = 1.0

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

def test_random_direction_gravity_mode():
    mode = RandomDirectionGravityMode()
    world = MockWorld()
    ball1 = MockBall("b1", 0.0, 0.0)
    balls = [ball1]

    mode.setup(world, balls)
    mode.shift_timer = 0.1 # Trigger shift soon

    # Tick to trigger shift
    mode.tick(world, balls, 0.15)

    assert mode.shift_duration > 0
    assert mode.shift_dx != 0.0 or mode.shift_dy != 0.0
    assert len(world.events) > 0
    assert world.events[0][0] == "random_direction_gravity_shift"

    # Tick with gravity active
    initial_vx_b1 = ball1.vx
    initial_vy_b1 = ball1.vy

    mode.tick(world, balls, 0.1)

    # Ball 1 should have changed velocity in the random direction
    assert ball1.vx != initial_vx_b1 or ball1.vy != initial_vy_b1

    expected_vx = initial_vx_b1 + mode.shift_dx * mode.shift_strength * 0.1
    expected_vy = initial_vy_b1 + mode.shift_dy * mode.shift_strength * 0.1

    assert abs(ball1.vx - expected_vx) < 0.0001
    assert abs(ball1.vy - expected_vy) < 0.0001
