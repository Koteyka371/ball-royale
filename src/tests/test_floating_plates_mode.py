import pytest
from ai.game_modes import FloatingPlatesMode

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 100.0
        self.is_alive = True

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.is_alive = False

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

def test_floating_plates_setup():
    mode = FloatingPlatesMode()
    world = MockWorld()
    mode.setup(world, [])
    assert len(mode.plates) == 5
    assert mode.plates[4]["x"] == 500.0
    assert mode.plates[4]["y"] == 500.0
    assert mode.plates[4]["radius"] == 250.0

def test_floating_plates_damage():
    mode = FloatingPlatesMode()
    world = MockWorld()
    b_safe = MockBall(500, 500)
    b_abyss = MockBall(0, 0)
    mode.setup(world, [b_safe, b_abyss])

    mode.tick(world, [b_safe, b_abyss], 1.0)
    assert b_safe.hp == 100.0
    assert b_abyss.hp == 50.0

def test_floating_plates_shrink():
    mode = FloatingPlatesMode()
    world = MockWorld()
    mode.setup(world, [])

    initial_radius = mode.plates[4]["radius"]
    mode.shrink_interval = 0.5
    mode.tick(world, [], 0.6)

    assert mode.plates[4]["radius"] < initial_radius

def test_floating_plates_tilt():
    mode = FloatingPlatesMode()
    world = MockWorld()
    b = MockBall(500, 500)
    mode.setup(world, [b])

    # Force tilt
    mode.tilt_timer = mode.tilt_interval
    # Monkeypatch random to always tilt
    mode.random.random = lambda: 0.1
    mode.random.uniform = lambda a, b: 50.0

    initial_x = b.x
    mode.tick(world, [b], 1.0)

    # Check if ball moved due to tilt
    assert b.x > initial_x
