import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

class MockBall:
    def __init__(self, id_val):
        self.x = 0.0
        self.y = 0.0
        self._id = id_val
    def get_instance_id(self):
        return self._id

    @property
    def id(self):
        return self._id

def test_expanding_arena_mode_initial_setup():
    mode = GAME_MODES.get("expanding_arena")
    assert mode is not None, "Mode should exist"

    world = MockWorld()
    balls = [MockBall(1), MockBall(2)]

    mode.setup(world, balls)

    # Check if initial shrinking happened
    assert world.arena.width == 400.0
    assert world.arena.height == 400.0

    # Check if balls are repositioned near center
    for b in balls:
        assert 150.0 <= b.x <= 250.0
        assert 150.0 <= b.y <= 250.0

def test_expanding_arena_mode_expansion():
    mode = GAME_MODES.get("expanding_arena")

    world = MockWorld()
    balls = [MockBall(1)]
    mode.setup(world, balls)

    assert world.arena.width == 400.0

    # Should not expand immediately
    mode.tick(world, balls, delta=5.0)
    assert world.arena.width == 400.0

    # Should expand after passing the threshold (10.0)
    mode.tick(world, balls, delta=6.0)

    # 400 * 1.2 = 480
    assert world.arena.width == 480.0
    assert world.arena.height == 480.0

    # Should also spawn a hazard
    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert hasattr(hazard, "x")

    # Should create a visual effect event
    assert len(world.events) == 1
    assert world.events[0]['type'] == 'visual_effect'
