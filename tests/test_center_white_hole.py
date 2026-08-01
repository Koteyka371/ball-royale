import pytest
from unittest.mock import MagicMock
from src.ai.game_modes import CenterWhiteHoleMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, x, y, hp=100.0):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 15.0
        self.hp = hp
        self.alive = True
        self.ball_type = "normal"
        self.killer = None

def test_center_white_hole_setup():
    mode = CenterWhiteHoleMode()
    world = MockWorld()

    mode.setup(world, [])

    assert len(world.arena.hazards) == 1
    wh = world.arena.hazards[0]
    assert getattr(wh, "kind") == "white_hole"
    assert getattr(wh, "x") == 500.0
    assert getattr(wh, "y") == 500.0
    assert getattr(wh, "radius") == 10.0
    assert mode.min_x == 0.0
    assert mode.max_x == 1000.0
    assert mode.min_y == 0.0
    assert mode.max_y == 1000.0

def test_center_white_hole_tick_growth_and_push():
    mode = CenterWhiteHoleMode()
    world = MockWorld()
    mode.setup(world, [])

    # Ball directly to the right of the center
    b1 = MockBall(600.0, 500.0)

    # Delta of 1 second for easy math
    mode.tick(world, [b1], delta=1.0)

    wh = world.arena.hazards[0]
    # Check growth
    assert getattr(wh, "radius") == 10.0 + mode.growth_rate

    # Check push
    # Ball is at 600, WH is at 500. dx = 100, dy = 0, dist = 100.
    # push_strength increases by 10 per second: 200 + 10 = 210.
    # push_x = (100 / 100) * 210 * 1 = 210
    assert b1.vx == 210.0
    assert b1.vy == 0.0

def test_center_white_hole_shrinks_and_damages_outside_bounds():
    mode = CenterWhiteHoleMode()
    world = MockWorld()
    mode.setup(world, [])

    b1 = MockBall(990.0, 500.0, hp=5.0)

    # Shrink boundaries by 10 in all directions
    # Boundary will be min_x=10, max_x=990
    # b1 is at 990, radius is 15. 990 + 15 = 1005 > 990. So b1 is outside.
    mode.tick(world, [b1], delta=1.0)

    assert mode.min_x == 10.0
    assert mode.max_x == 990.0
    assert mode.min_y == 10.0
    assert mode.max_y == 990.0

    # b1 hp should be 5 - 10 = -5 -> 0, dead
    assert b1.hp == 0.0
    assert b1.alive == False
    assert b1.killer == "Shrinking Boundary"

def test_center_white_hole_no_push_if_dead():
    mode = CenterWhiteHoleMode()
    world = MockWorld()
    mode.setup(world, [])

    b1 = MockBall(600.0, 500.0)
    b1.alive = False

    mode.tick(world, [b1], delta=1.0)

    assert b1.vx == 0.0
    assert b1.vy == 0.0
