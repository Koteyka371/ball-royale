import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/ai')))

from src.ai.game_modes import HotPotatoMode

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, id_val, x, y):
        self.id = id_val
        self.x = x
        self.y = y
        self.alive = True

def test_hot_potato_mode_setup():
    mode = HotPotatoMode()
    world = MockWorld()
    balls = [MockBall(1, 10, 10), MockBall(2, 20, 20)]

    mode.setup(world, balls)

    assert len(world.arena.hazards) == 1
    bomb = world.arena.hazards[0]
    assert getattr(bomb, "kind", "") == "sticky_bomb"
    assert getattr(bomb, "attached_id", None) in [1, 2]

def test_hot_potato_mode_tick_respawns_bomb():
    mode = HotPotatoMode()
    world = MockWorld()
    balls = [MockBall(1, 10, 10)]

    # tick should spawn one if not present
    mode.tick(world, balls, 0.1)

    assert len(world.arena.hazards) == 1
    bomb = world.arena.hazards[0]
    assert getattr(bomb, "kind", "") == "sticky_bomb"
    assert getattr(bomb, "attached_id", None) == 1

def test_hot_potato_mode_tick_keeps_bomb():
    mode = HotPotatoMode()
    world = MockWorld()
    balls = [MockBall(1, 10, 10)]

    mode.setup(world, balls)
    assert len(world.arena.hazards) == 1

    # Tick should not spawn a second one
    mode.tick(world, balls, 0.1)

    assert len(world.arena.hazards) == 1
