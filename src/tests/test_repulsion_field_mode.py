import pytest
from ai.game_modes import GAME_MODES

def test_repulsion_field_mode():
    assert "repulsion_field" in GAME_MODES
    mode = GAME_MODES["repulsion_field"]

    class MockBall:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.vx = 0.0
            self.vy = 0.0
            self.alive = True
            self.ball_type = "normal"

    b1 = MockBall(100, 100)
    b2 = MockBall(150, 100)

    class MockWorld:
        pass

    world = MockWorld()

    # Distance is 50, within max_dist of 300
    mode.tick(world, [b1, b2], delta=0.1)

    # Repulsion force should push b1 left (vx < 0) and b2 right (vx > 0)
    assert b1.vx < 0
    assert b2.vx > 0

    # Verify no vertical movement since they are horizontally aligned
    assert b1.vy == 0
    assert b2.vy == 0

    # Test distance > 300
    b3 = MockBall(100, 100)
    b4 = MockBall(500, 100)

    mode.tick(world, [b3, b4], delta=0.1)
    assert b3.vx == 0
    assert b4.vx == 0
