import pytest
import math
from ai.game_modes import RoamingBlackHoleMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.weather = "normal"

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []

class MockBall:
    def __init__(self, x, y, alive=True):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.alive = alive
        self.hp = 100.0
        self.ball_type = "normal"
        self.gravity_multiplier = 1.0
        self.mass = 1.0

def test_roaming_black_hole_setup():
    mode = RoamingBlackHoleMode()
    world = MockWorld()
    mode.setup(world, [])
    assert mode.bh_x == 500.0
    assert mode.bh_y == 500.0

def test_roaming_black_hole_bounces():
    mode = RoamingBlackHoleMode()
    world = MockWorld()
    mode.setup(world, [])

    # Move near right edge
    mode.bh_x = 950.0
    mode.bh_vx = 100.0
    mode.tick(world, [], delta=1.0)
    assert mode.bh_vx == -100.0

def test_roaming_black_hole_pulls_and_kills():
    mode = RoamingBlackHoleMode()
    world = MockWorld()
    mode.setup(world, [])

    # After 1.0s delta, bh moves from 500,500 by (150,100) -> 650, 600

    ball_kill = MockBall(650, 600)  # Will be exactly on BH
    ball_pull = MockBall(800, 600)  # Dist 150 > 80 radius

    mode.tick(world, [ball_kill, ball_pull], delta=1.0)

    assert not ball_kill.alive
    assert ball_kill.hp == 0

    # ball_pull should move towards (650, 600) via velocity
    # dx = 650 - 800 = -150. pull_strength = 2000000 / (150*150) = 2000000/22500 = 88.88
    # b.vx += (dx/dist)*pull*1.0 = (-1) * 88.88 * 1.0 = -88.88
    assert ball_pull.vx < 0.0
    assert ball_pull.alive
