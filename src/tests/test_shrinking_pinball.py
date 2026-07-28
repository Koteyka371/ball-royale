
import pytest
from ai.game_modes import ShrinkingPinballMode

class MockArena:
    def __init__(self, width=1000.0, height=1000.0):
        self.width = width
        self.height = height
        self.hazards = []

class MockWorld:
    def __init__(self, arena=None):
        self.arena = arena if arena else MockArena()
        self.projectiles = []

class MockEntity:
    def __init__(self, x=500.0, y=500.0, vx=0.0, vy=0.0, radius=15.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.alive = True
        self.hp = 1.0
        self.bounces = 0

def test_shrinking_pinball_shrinks_and_bounces():
    mode = ShrinkingPinballMode()
    world = MockWorld()

    # Place entity near right edge, moving right
    ent = MockEntity(x=990.0, y=500.0, vx=100.0, vy=0.0, radius=15.0)
    balls = [ent]

    delta = 1.0 # 1 second tick for big shrink
    mode.tick(world, balls, delta)

    assert world.arena.width == 990.0
    assert world.arena.height == 990.0

    # Entity should have bounced and moved inside
    assert ent.x == 990.0 - 15.0
    assert ent.vx < 0.0 # Bounced left
    assert abs(ent.vx) > 100.0 * 1.2 # Should have increased speed based on multiplier
    assert ent.bounces == 1

    # Test projectile that goes beyond bounds (e.g. left and top)
    # The shrink happens in tick, then the bounds are checked
    proj = MockEntity(x=4.0, y=4.0, vx=-50.0, vy=-50.0, radius=5.0)
    world.projectiles.append(proj)

    mode.tick(world, balls, delta)

    # It should bounce off top and left walls
    assert proj.vx > 0.0
    assert proj.vy > 0.0
    assert proj.bounces >= 1
