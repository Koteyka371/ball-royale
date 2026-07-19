import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self, width=1000, height=1000):
        self.width = width
        self.height = height

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.dead_balls = []

class MockBall:
    def __init__(self, id_val, btype="warrior"):
        self.id = id_val
        self.ball_type = btype
        self.alive = True
        self.x = 500.0
        self.y = 500.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.team = btype

def test_shrinking_boundary_mode():
    mode = GAME_MODES.get("shrinking_boundary")
    assert mode is not None
    world = MockWorld()
    balls = [MockBall(0), MockBall(1)]
    mode.setup(world, balls)

    # Initial boundaries
    assert mode.min_x == 0.0
    assert mode.max_x == 1000.0
    assert mode.min_y == 0.0
    assert mode.max_y == 1000.0

    # Tick and check shrinking
    mode.tick(world, balls, delta=1.0)
    assert mode.min_x > 0.0
    assert mode.max_x < 1000.0
    assert mode.min_y > 0.0
    assert mode.max_y < 1000.0

    # Balls inside should not take damage
    assert balls[0].hp == 100.0

    # Move ball out of bounds
    balls[0].x = 1000.0
    balls[0].y = 1000.0
    initial_hp = balls[0].hp
    mode.tick(world, balls, delta=1.0)

    # Ball should have taken damage
    assert balls[0].hp == 80.0
    assert balls[0].alive is True

    # Deal enough damage to kill
    balls[0].hp = 1.0
    mode.tick(world, balls, delta=1.0)
    assert not balls[0].alive
    assert balls[0].killer == "Shrinking Boundary"
