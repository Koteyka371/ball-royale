import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []

class MockBall:
    def __init__(self, x, y, hp=100.0, alive=True):
        self.x = x
        self.y = y
        self.hp = hp
        self.alive = alive
        self.vx = 0.0
        self.vy = 0.0
        self.killer = None
        self.id = id(self)

def test_pulsing_black_hole_mutator():
    assert "pulsing_black_hole_mutator" in GAME_MODES
    mode = GAME_MODES["pulsing_black_hole_mutator"]

    world = MockWorld()
    b1 = MockBall(550.0, 500.0)
    balls = [b1]

    mode.setup(world, balls)

    assert len(world.arena.hazards) == 1
    bh = world.arena.hazards[0]
    assert getattr(bh, "kind") == "pulsing_black_hole"
    assert getattr(bh, "radius") == 30.0

    # Advance time to before pulsing
    mode.tick(world, balls, delta=4.9)
    assert not mode.is_pulsing
    assert b1.hp == 100.0
    assert getattr(bh, "radius") == 30.0

    # Trigger pulse
    mode.tick(world, balls, delta=0.2)
    assert mode.is_pulsing
    assert getattr(bh, "radius") == 80.0

    assert b1.hp < 100.0
    assert b1.vx > 0.0  # Pushed away

    # End pulse
    mode.tick(world, balls, delta=1.0)
    assert not mode.is_pulsing
    assert getattr(bh, "radius") == 30.0
