import pytest
from ai.game_modes import ShrinkingBoundaryMode

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
        self.alive = True
        self.ball_type = "normal"
        self.x = x
        self.y = y
        self.hp = 100.0
        self.killer = None

def test_shrinking_boundary_elimination():
    mode = ShrinkingBoundaryMode()
    world = MockWorld()

    ball_inside = MockBall(500, 500)
    ball_outside = MockBall(-100, 500)

    balls = [ball_inside, ball_outside]

    mode.setup(world, balls)

    # Tick for 1 second, ball should lose 20 HP
    mode.tick(world, balls, 1.0)

    assert ball_inside.alive is True
    assert ball_inside.hp == 100.0

    assert ball_outside.alive is True
    assert ball_outside.hp == 80.0

    # Tick for another 4 seconds, ball should lose 80 HP and die
    mode.tick(world, balls, 4.0)

    assert ball_outside.alive is False
    assert ball_outside.hp == 0.0
    assert ball_outside.killer == "Shrinking Boundary"

if __name__ == "__main__":
    pytest.main([__file__])
