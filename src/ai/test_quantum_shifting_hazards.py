import pytest
import math
from ai.game_modes import GAME_MODES

class MockEntity:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 10
        self.alive = True
        self.ball_type = "basic"

class MockHazard:
    def __init__(self, id, x, y, radius, kind):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.damage = 10.0
        self.active = True

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = [MockHazard("h1", 100, 100, 30, "spikes")]

class MockWorld:
    def __init__(self):
        self.tick = 0
        self.arena = MockArena()
        self.balls = [MockEntity(1, 100, 100)]
        self.events = []

    def add_event(self, event_type, data):
        pass

def test_quantum_shifting_mode():
    import random
    import unittest.mock
    with unittest.mock.patch('random.random', return_value=0.1):
        mode = GAME_MODES["quantum_shifting_hazards"]
        world = MockWorld()

        # Tick to overlap and shift the hazard
        mode.tick(world, world.balls, 0.1)
        assert world.arena.hazards[0].kind == "quantum_teleporter"
        assert hasattr(world.arena.hazards[0], "target_x")

    # Move ball away
        world.balls[0].x = 500
        world.balls[0].y = 500

        # Tick past 5 seconds
        mode.tick(world, world.balls, 5.1)
        assert world.arena.hazards[0].kind == "spikes"

if __name__ == "__main__":
    test_quantum_shifting_mode()
