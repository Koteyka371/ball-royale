import math
from ai.game_modes import GAME_MODES

def test_mini_black_holes():
    mode = GAME_MODES["mini_black_holes"]
    assert mode.name == "Mini Black Holes"

    class MockArena:
        def __init__(self):
            self.width = 1000.0
            self.height = 1000.0
            self.hazards = []

    class MockWorld:
        def __init__(self):
            self.arena = MockArena()

    class MockBall:
        def __init__(self):
            self.x = 500.0
            self.y = 500.0
            self.vx = 0.0
            self.vy = 0.0
            self.alive = True

    world = MockWorld()
    ball1 = MockBall()
    ball1.x = 200.0
    ball1.y = 200.0
    balls = [ball1]

    # Tick until spawn
    for _ in range(600):
        mode.tick(world, balls, 0.016)

    assert len(world.arena.hazards) > 0
    bh = world.arena.hazards[0]
    assert getattr(bh, "is_mini_bh", False)
