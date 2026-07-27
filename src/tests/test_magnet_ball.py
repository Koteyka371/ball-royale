import pytest
from ai.magnet_ball import MagnetBallMode

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
    def add_event(self, kind, data):
        self.events.append((kind, data))

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.alive = True
        self.ball_type = "basic"

def test_magnet_ball_mode_setup():
    mode = MagnetBallMode()
    world = MockWorld()
    balls = []

    mode.setup(world, balls)
    assert len(world.arena.hazards) == 1
    assert getattr(world.arena.hazards[0], "kind", "") == "magnetizer"

def test_magnet_ball_mode_attract():
    mode = MagnetBallMode()
    world = MockWorld()

    b1 = MockBall(1, 100.0, 100.0)
    b1.magnet_charge = 1

    b2 = MockBall(2, 200.0, 100.0)
    b2.magnet_charge = -1

    balls = [b1, b2]

    mode.setup(world, balls)
    mode.apply_dynamic_traits(world, balls, delta=0.1)

    # Distance started at 100
    dist = abs(b2.x - b1.x)
    assert dist < 100.0

def test_magnet_ball_mode_repel():
    mode = MagnetBallMode()
    world = MockWorld()

    b1 = MockBall(1, 100.0, 100.0)
    b1.magnet_charge = 1

    b2 = MockBall(2, 200.0, 100.0)
    b2.magnet_charge = 1

    balls = [b1, b2]

    mode.setup(world, balls)
    mode.apply_dynamic_traits(world, balls, delta=0.1)

    # Distance started at 100
    dist = abs(b2.x - b1.x)
    assert dist > 100.0

def test_magnet_ball_mode_pulse():
    mode = MagnetBallMode()
    world = MockWorld()

    b1 = MockBall(1, 100.0, 100.0)
    balls = [b1]

    mode.setup(world, balls)
    mode.pulse_timer = 4.9
    mode.apply_dynamic_traits(world, balls, delta=0.2)

    # Timer should wrap and assign a charge
    assert mode.pulse_timer == 0.0
    assert hasattr(b1, "magnet_charge")
    assert b1.magnet_charge in [-1, 1]
    assert any(e[0] == "magnet_charge_changed" for e in world.events)
