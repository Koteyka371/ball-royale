import pytest
from unittest.mock import MagicMock
from ai.game_modes import ShrinkingArenaMode

class MockArena:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.hazards = []

class MockWorld:
    def __init__(self, arena):
        self.arena = arena
        self.events = []

    def add_event(self, name, data):
        self.events.append((name, data))

class MockBall:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.alive = True

def test_shrinking_arena_mode():
    mode = ShrinkingArenaMode()
    arena = MockArena(1000.0, 1000.0)
    world = MockWorld(arena)

    # 2 balls: one inside bounds, one at the very edge
    b1 = MockBall(500.0, 500.0, 15.0)
    b2 = MockBall(990.0, 990.0, 15.0)
    balls = [b1, b2]

    # Tick for 29.9 seconds (should not shrink yet)
    mode.tick(world, balls, 29.9)
    assert arena.width == 1000.0
    assert arena.height == 1000.0
    assert b2.x == 990.0

    # Tick 0.2 more seconds to trigger shrink
    mode.tick(world, balls, 0.2)

    assert arena.width == 900.0
    assert arena.height == 900.0

    # Check bounds pushing
    assert b1.x == 500.0 # Untouched
    assert b2.x == 900.0 - 15.0 # Pushed back to new bounds (900 - 15 = 885)
    assert b2.y == 885.0

    # Check event
    assert len(world.events) == 1
    assert world.events[0][0] == "arena_shrunk"
    assert world.events[0][1]["width"] == 900.0

def test_shrinking_arena_minimum_size():
    mode = ShrinkingArenaMode()
    arena = MockArena(210.0, 210.0)
    world = MockWorld(arena)
    balls = []

    # Shrink triggers
    mode.tick(world, balls, 30.0)

    # Should clamp to 200.0 (210 * 0.9 = 189, clamped to 200)
    assert arena.width == 200.0
    assert arena.height == 200.0
