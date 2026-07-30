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
        self.events = []

    def add_event(self, type_name, data):
        self.events.append({"type": type_name, "data": data})

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 100.0
        self.alive = True
        self.damage = 10.0
        self.base_damage = 10.0
        self.z_layer = 1
        self.waterfall_fall_timer = 0.0

def test_waterfalls_mode_hazards_and_falling_restore():
    assert "waterfalls_mode" in GAME_MODES
    mode = GAME_MODES["waterfalls_mode"]

    world = MockWorld()
    ball1 = MockBall(500, 500)
    balls = [ball1]

    mode.setup(world, balls)

    # Force tick past spawn timer to spawn waterfall at center (by setting fixed random)
    class FakeRandom:
        def uniform(self, a, b):
            return 500.0
        def randint(self, a, b):
            return 1234

    mode.random = FakeRandom()
    mode.spawn_timer = 0.0
    mode.tick(world, balls, 0.1)

    assert len(world.arena.hazards) == 1

    # Test pulling and falling effect
    ball1.x = 505.0
    ball1.y = 500.0

    # Tick with delta 0.1
    mode.tick(world, balls, 0.1)

    assert getattr(ball1, "waterfall_fall_timer", 0.0) == 2.0
    assert getattr(ball1, "z_layer", 1) == 0

    # Tick again to let the state update
    mode.tick(world, balls, 0.1)
    assert ball1.damage == 0.0
    assert ball1.base_damage == 0.0

    # Move ball far away so it doesn't get reset
    ball1.x = 1000.0
    ball1.y = 1000.0

    # Fast forward to expire the timer
    mode.tick(world, balls, 2.0)

    # Timer should be 0, damage should be restored
    assert getattr(ball1, "waterfall_fall_timer", 0.0) == 0.0
    assert ball1.damage == 10.0
    assert ball1.base_damage == 10.0
