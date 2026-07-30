import pytest
from ai.game_modes import MiniBlackHolesMode

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.id = "b1"

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

def test_mini_black_holes_mode():
    mode = MiniBlackHolesMode()
    world = MockWorld()
    b1 = MockBall(500, 500)
    balls = [b1]

    # Tick to spawn a black hole
    for _ in range(600): # > 8 seconds at 0.016 delta (5.0 initial timer)
        mode.tick(world, balls, 0.016)

    assert len(world.arena.hazards) > 0
    bh = world.arena.hazards[0]

    assert bh.kind in ["mini_black_hole", "black_hole"]
    assert getattr(bh, "is_mini_bh", False)

    # Move ball near black hole and see if it gets pulled
    b1.x = bh.x + 50
    b1.y = bh.y
    b1.vx = 0
    b1.vy = 0

    mode.tick(world, balls, 0.016)
    # Pull should be negative x since ball is to the right
    assert b1.vx < 0
    assert b1.vy == 0
