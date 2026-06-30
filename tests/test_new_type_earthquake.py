import pytest
from unittest.mock import MagicMock
from ai.game_modes import EarthquakeMode

class MockBall:
    def __init__(self, id_val, x, y, hp, ball_type):
        self.id = id_val
        self.x = x
        self.y = y
        self.hp = hp
        self.ball_type = ball_type
        self.alive = True
        self.vx = 0.0
        self.vy = 0.0

def test_earthquake_mode_trigger_and_shake():
    mode = EarthquakeMode()
    world = MagicMock()
    world.add_event = MagicMock()

    ball = MockBall(1, 100.0, 100.0, 100, "warrior")
    balls = [ball]

    # Fast forward timer to trigger earthquake
    mode.timer = 11.0
    # Mock random to ensure earthquake triggers
    import random
    original_random = random.random
    random.random = lambda: 0.0  # Force < 0.2 * delta

    mode.tick(world, balls, delta=1.0)

    random.random = original_random

    assert mode.is_shaking == True
    assert mode.shake_timer > 0
    world.add_event.assert_called_once()

    # Now simulate shake applying impulses
    orig_x, orig_y = ball.x, ball.y
    # Force random to apply a fixed impulse
    original_uniform = random.uniform
    # Notice: lambda *args in tests for MockRandom when mocked!
    random.uniform = lambda *args: 10.0

    mode.tick(world, balls, delta=1.0)

    random.uniform = original_uniform

    assert mode.shake_timer >= 0
    assert ball.x != orig_x
    assert ball.y != orig_y
    assert ball.vx != 0.0
    assert ball.vy != 0.0
