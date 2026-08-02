import pytest
from unittest.mock import MagicMock
from ai.game_modes import ExpandingArenaMode

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

def test_expanding_arena_mode():
    mode = ExpandingArenaMode()
    arena = MockArena(500.0, 500.0)
    world = MockWorld(arena)

    b1 = MockBall(250.0, 250.0, 15.0)
    balls = [b1]

    # Tick for 29.9 seconds (should not expand yet)
    mode.tick(world, balls, 29.9)
    assert arena.width == 500.0
    assert arena.height == 500.0

    # Tick 0.2 more seconds to trigger expand
    mode.tick(world, balls, 0.2)

    assert arena.width == 550.0 # 500 * 1.1 = 550
    assert arena.height == 550.0

    # Check event
    assert len(world.events) == 1
    assert world.events[0][0] == "arena_expanded"
    assert world.events[0][1]["width"] == 550.0

def test_expanding_arena_maximum_size():
    mode = ExpandingArenaMode()
    arena = MockArena(1900.0, 1900.0)
    world = MockWorld(arena)
    balls = []

    # Expand triggers
    mode.tick(world, balls, 30.0)

    # Should clamp to 2000.0 (1900 * 1.1 = 2090, clamped to 2000)
    assert arena.width == 2000.0
    assert arena.height == 2000.0
