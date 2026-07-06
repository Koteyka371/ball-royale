import pytest
from ai.reverse_friction import ReverseFrictionMode

class MockBall:
    def __init__(self, id, x, y, vx=0.0, vy=0.0):
        self.id = id
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.alive = True
        self.damage = 10.0
        self.speed = 100.0
        self.base_damage = 10.0
        self.base_speed = 10.0

class MockWorld:
    def __init__(self):
        self.events = []
    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_reverse_friction_increases_speed():
    mode = ReverseFrictionMode()
    world = MockWorld()
    # High enough speed so ratio > 1
    ball = MockBall(1, 0, 0, 150.0, 0.0)

    mode.setup(world, [ball])
    assert ball.is_frictionless is True

    # Tick with movement
    initial_vx = ball.vx
    mode.tick(world, [ball], 0.1)

    # Check that vx increased (acceleration)
    assert ball.vx > initial_vx

    # Check that damage increased due to speed
    assert ball.damage > ball.base_damage

def test_reverse_friction_damage_caps():
    mode = ReverseFrictionMode()
    world = MockWorld()
    # High speed to trigger max damage multiplier
    ball = MockBall(1, 0, 0, 1000.0, 0.0)

    mode.setup(world, [ball])

    mode.tick(world, [ball], 0.1)

    # Speed is very high, so ratio > 5. Damage should cap at 5x base
    assert ball.damage == 50.0

def test_reverse_friction_idle():
    mode = ReverseFrictionMode()
    world = MockWorld()
    ball = MockBall(1, 0, 0, 0.0, 0.0)

    mode.setup(world, [ball])

    mode.tick(world, [ball], 0.1)

    # Should not accelerate
    assert ball.vx == 0.0
    assert ball.vy == 0.0
    # Damage should be base
    assert ball.damage == 10.0
