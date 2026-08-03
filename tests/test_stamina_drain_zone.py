import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.hazards = []

class MockWorld:
    def __init__(self, width=1000, height=1000):
        self.arena = MockArena(width, height)

class MockBall:
    def __init__(self, x, y, alive=True, stamina=100.0):
        self.x = x
        self.y = y
        self.alive = alive
        self.stamina = stamina

def test_stamina_drain_zone_mode():
    assert "stamina_drain_zone" in GAME_MODES
    mode = GAME_MODES["stamina_drain_zone"]

    world = MockWorld()
    ball1 = MockBall(x=500.0, y=500.0, stamina=100.0) # Inside zone
    ball2 = MockBall(x=100.0, y=100.0, stamina=100.0) # Outside zone

    mode.setup(world, [ball1, ball2])

    assert mode.zone_x == 500.0
    assert mode.zone_y == 500.0

    # Check hazard appended
    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].kind == "stamina_drain_zone"

    mode.tick(world, [ball1, ball2], delta=1.0)

    assert ball1.stamina == 100.0 - 15.0  # inside, drained
    assert ball2.stamina == 100.0  # outside, untouched
