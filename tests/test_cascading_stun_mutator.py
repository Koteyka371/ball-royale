import pytest
from ai.game_modes import CascadingStunMutatorMode
from ai.action import Action
import math

class MockBall:
    def __init__(self, x, y, radius=10):
        self.x = x
        self.y = y
        self.radius = radius
        self.is_alive = True
        self.stun_explosion_armed = False
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 0.0
        self.base_speed = 100.0

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __contains__(self, key):
        return hasattr(self, key)

    def get(self, key, default=None):
        return getattr(self, key, default)

class MockWorld:
    def __init__(self):
        self.arena = type('MockArena', (), {'width': 1000, 'height': 1000})()

def test_cascading_stun_mutator_arming():
    mode = CascadingStunMutatorMode()
    world = MockWorld()

    # Create two balls that are colliding
    ball1 = MockBall(0, 0)
    ball2 = MockBall(10, 10)
    # distance squared = 200, sum of radii = 20 (squared = 400), so they are colliding

    balls = [ball1, ball2]

    mode.tick(world, balls, 0.1)

    assert ball1.stun_explosion_armed is True
    assert ball2.stun_explosion_armed is True

def test_cascading_stun_mutator_no_collision():
    mode = CascadingStunMutatorMode()
    world = MockWorld()

    # Create two balls that are far apart
    ball1 = MockBall(0, 0)
    ball2 = MockBall(100, 100)

    balls = [ball1, ball2]

    mode.tick(world, balls, 0.1)

    assert ball1.stun_explosion_armed is False
    assert ball2.stun_explosion_armed is False
