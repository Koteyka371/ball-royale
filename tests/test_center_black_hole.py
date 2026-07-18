import pytest
from unittest.mock import MagicMock
from src.ai.game_modes import CenterBlackHoleMode
from src.arena.procedural_arena import Hazard

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True

def test_center_black_hole_setup():
    mode = CenterBlackHoleMode()
    world = MockWorld()

    mode.setup(world, [])

    assert len(world.arena.hazards) == 1
    bh = world.arena.hazards[0]
    assert getattr(bh, "kind") == "black_hole"
    assert getattr(bh, "x") == 500.0
    assert getattr(bh, "y") == 500.0
    assert getattr(bh, "radius") == 10.0

def test_center_black_hole_tick_growth_and_pull():
    mode = CenterBlackHoleMode()
    world = MockWorld()
    mode.setup(world, [])

    b1 = MockBall(100.0, 500.0) # Directly to the left of the center

    # Delta of 1 second for easy math
    mode.tick(world, [b1], delta=1.0)

    bh = world.arena.hazards[0]
    # Check growth
    assert getattr(bh, "radius") == 10.0 + mode.growth_rate

    # Check pull
    # Ball is at 100, BH is at 500. dx = 400. dy = 0. dist = 400
    # pull_factor = pull_strength / max(100, 400) = 200 / 400 = 0.5? Wait, my implementation had:
    # b.vx += (dx / dist) * pull_strength * delta -> b.vx += (400/400) * (200 + 10) * 1 = 210
    assert b1.vx == 210.0
    assert b1.vy == 0.0

def test_center_black_hole_no_pull_if_dead():
    mode = CenterBlackHoleMode()
    world = MockWorld()
    mode.setup(world, [])

    b1 = MockBall(100.0, 500.0)
    b1.alive = False

    mode.tick(world, [b1], delta=1.0)

    assert b1.vx == 0.0
