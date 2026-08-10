import pytest
import os
import sys

# Add src to PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))))

from ai.game_modes import LowGravityZoneMode
from collections import namedtuple

class DummyArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class DummyWorld:
    def __init__(self):
        self.arena = DummyArena()

class DummyBall:
    def __init__(self, x, y, mass=1.0, vy=100.0, alive=True, ball_type="player"):
        self.x = x
        self.y = y
        self.mass = mass
        self.vy = vy
        self.alive = alive
        self.ball_type = ball_type

def test_low_gravity_zone_active():
    mode = LowGravityZoneMode()
    world = DummyWorld()

    # Ball inside zone (center is 500, 500, radius is 250)
    b_inside = DummyBall(500.0, 500.0, mass=2.0, vy=50.0)

    # Ball outside zone
    b_outside = DummyBall(100.0, 100.0, mass=2.0, vy=50.0)

    balls = [b_inside, b_outside]

    delta = 0.016
    mode.tick(world, balls, delta)

    assert b_inside._low_gravity_zone_active is True
    assert b_inside.mass == 2.0 * 0.2
    assert b_inside.vy == max(0.0, 50.0 - 1200.0 * delta)

    assert getattr(b_outside, '_low_gravity_zone_active', False) is False
    assert b_outside.mass == 2.0
    assert b_outside.vy == 50.0

def test_low_gravity_zone_exit():
    mode = LowGravityZoneMode()
    world = DummyWorld()

    b = DummyBall(500.0, 500.0, mass=2.0, vy=50.0)

    # First tick, ball is inside
    mode.tick(world, [b], 0.016)
    assert b._low_gravity_zone_active is True
    assert b.mass == 2.0 * 0.2

    # Move outside
    b.x = 100.0
    b.y = 100.0

    # Second tick, ball is outside
    mode.tick(world, [b], 0.016)
    assert b._low_gravity_zone_active is False
    assert b.mass == 2.0

print("Running tests...")
