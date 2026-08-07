import pytest
from unittest.mock import MagicMock
from ai.game_modes import DenseRegionMode

class MockArena:
    def __init__(self, width=1000.0, height=1000.0):
        self.width = width
        self.height = height

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

class MockBall:
    def __init__(self, id_val, x, y):
        self.id = id_val
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.friction_multiplier = 1.0
        self.skill_timer = 0.0
        self.team = "blue"

def test_dense_region_mode():
    mode = DenseRegionMode()
    world = MockWorld()

    # Ball inside the region (radius 300 from center 500,500)
    # Center is at 500,500. A ball at 400, 500 is 100 units away.
    b_in = MockBall(1, 400.0, 500.0)
    b_in.skill_timer = 2.0  # Should be incremented

    # Ball outside the region (e.g. 500 units away)
    b_out = MockBall(2, 0.0, 500.0)
    b_out.skill_timer = 2.0 # Should not be incremented

    balls = [b_in, b_out]

    # delta = 0.016
    # b_in should be pulled towards 500, 500 -> vx should increase (since dx = 500 - 400 = 100, which is positive)
    # b_in should have friction_multiplier set to 3.0
    # b_in skill timer should increase by 2.0 * delta = 0.032

    mode.tick(world, balls, delta=0.016)

    # Check b_in
    assert b_in.vx > 0.0
    assert b_in.friction_multiplier == 3.0
    assert abs(b_in.skill_timer - (2.0 + 0.016 * 2.0)) < 0.001

    # Check b_out
    assert b_out.vx == 0.0
    assert b_out.friction_multiplier == 1.0
    assert b_out.skill_timer == 2.0  # Unchanged by this logic

    # Test restoring friction
    # Move b_in outside the region
    b_in.x = 0.0
    b_in.y = 0.0

    # Remember current vx to see if it changes
    b_in_vx_before = b_in.vx

    mode.tick(world, balls, delta=0.016)

    # b_in should now have its friction restored to original (1.0)
    assert b_in.friction_multiplier == 1.0
    # its vx should not have changed
    assert b_in.vx == b_in_vx_before
    # its skill timer should not have increased this tick
    assert abs(b_in.skill_timer - 2.032) < 0.001
