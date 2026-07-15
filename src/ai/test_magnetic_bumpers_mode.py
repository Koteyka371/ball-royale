import pytest
from ai.game_modes import MagneticBumpersMode
from unittest.mock import MagicMock

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.name = "basic"
        self.width = 1000
        self.height = 1000

    def clamp_position(self, x, y, r):
        return (x, y, False)

class MockWorld:
    def __init__(self, hazards):
        self.arena = MockArena(hazards)
        self.events = []
    def add_event(self, kind, data):
        pass

class MockBumper:
    def __init__(self, id, x, y, kind):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 30.0

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.alive = True
        self.hp = 100
        self.max_hp = 100
        self.ball_type = "basic"
        self.traits = []
        self.speed = 100.0
        self.damage = 10.0

def test_magnetic_bumpers_mode_pull():
    mode = MagneticBumpersMode()

    # Create a bumper at (100, 100)
    bumper = MockBumper(1, 100.0, 100.0, "bumper")
    world = MockWorld([bumper])

    # Create a ball at (150, 100), distance = 50.0
    ball = MockBall(1, 150.0, 100.0)

    # Test pulling logic
    mode.tick(world, [ball], 0.1) # Pass a larger delta to see clear movement

    # The ball should move closer to (100, 100) -> its X should be < 150.0
    assert ball.x < 150.0
    assert ball.y == 100.0 # Y shouldn't change
