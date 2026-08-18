import pytest
from ai.game_modes import ExpandingArenaMode

class MockArena:
    def __init__(self):
        self.width = 500.0
        self.height = 500.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, name, data):
        self.events.append((name, data))

def test_expanding_arena_setup():
    mode = ExpandingArenaMode()
    world = MockWorld()

    world.arena.width = 1000.0
    world.arena.height = 1000.0
    mode.setup(world, [])

    # Should cap at 500.0 initial
    assert world.arena.width == 500.0
    assert world.arena.height == 500.0

def test_expanding_arena_tick():
    mode = ExpandingArenaMode()
    world = MockWorld()
    mode.setup(world, [])

    for _ in range(30):
        mode.tick(world, [], 1.0)

    assert world.arena.width == 550.0
    assert world.arena.height == 550.0

    event_names = [e[0] for e in world.events]
    assert "arena_expanded" in event_names
