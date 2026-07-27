import math
from ai.action import Action
import pytest

class MockWorld:
    def __init__(self):
        self.tick = 1
        self.arena = type('MockArena', (), {'hazards': [], 'weather': ''})()

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 10.0
        self.mass = 1.0
        self.speed = 100.0
        self.team = "A"

class MockHazard:
    def __init__(self, kind, x, y, radius):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.active = True
        self.is_disabled_by_flare = False

def test_shrink_ray_trap():
    world = MockWorld()
    ball = MockBall(1, 0, 0)
    trap = MockHazard("shrink_ray_trap", 0, 0, 10.0)
    world.arena.hazards.append(trap)

    action = Action(ball, world)
    action._resolve_collisions()

    assert ball.radius == 5.0
    assert ball.mass == 0.2
    assert ball.speed == 150.0
    assert getattr(ball, "is_shrunk", False) == True
    assert getattr(ball, "shrink_ray_timer", 0.0) == 5.0
    assert not trap.active

    # Tick down
    action.execute("idle", 2.0)
    assert getattr(ball, "shrink_ray_timer", 0.0) == 3.0
    assert getattr(ball, "is_shrunk", False) == True

    # Revert
    action.execute("idle", 3.0)
    assert getattr(ball, "shrink_ray_timer", 0.0) == 0.0
    assert getattr(ball, "is_shrunk", False) == False
    assert ball.radius == 10.0
    assert ball.mass == 1.0
    assert ball.speed == 100.0
