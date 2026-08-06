import pytest
from src.ai.game_modes import FactoryMode
from src.arena.arena_types import ConveyorBelt


class MockBall:
    def __init__(self):
        self.x = 500.0
        self.y = 500.0
        self.vx = 0.0
        self.vy = 0.0
        self.mass = 1.0

class MockWorld:
    def __init__(self):
        self.balls = [MockBall()]
        self.items = []

def test_factory_mode_conveyor():
    mode = FactoryMode()
    w = MockWorld()

    mode.arena.hazards = [
        ConveyorBelt(id=0, x=500.0, y=500.0, radius=100.0, damage=0.0, direction_vector=(1.0, 0.0), speed_magnitude=200.0)
    ]

    # FactoryMode uses tick, not update
    mode.tick(w, w.balls, 0.1)

    assert w.balls[0].vx > 0.0
