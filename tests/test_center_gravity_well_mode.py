import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.hp = 100.0

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

def test_center_gravity_well():
    mode = GAME_MODES.get("center_gravity_well")
    assert mode is not None

    world = MockWorld()
    # Center is at 500, 500
    # Place a ball at 250, 500 (distance = 250)
    b = MockBall(250.0, 500.0)

    mode.setup(world, [b])

    # Assert hazard is spawned
    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].kind == "center_gravity_well"

    mode.tick(world, [b], 1.0)

    # Ball should be pulled towards center (+x direction)
    assert b.vx > 0.0, "Ball should have positive x velocity"
    assert b.vy == 0.0, "Ball should have 0 y velocity"

def test_center_gravity_well_damage():
    mode = GAME_MODES.get("center_gravity_well")
    world = MockWorld()
    # Place ball exactly at center (distance = 0, inside horizon)
    b = MockBall(500.0, 500.0)

    mode.setup(world, [b])
    mode.tick(world, [b], 1.0)

    # Should take damage
    assert b.hp < 100.0, "Ball inside event horizon should take damage"
