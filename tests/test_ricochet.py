import pytest
from src.ai.ricochet import RicochetMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.projectiles = []

class MockBall:
    def __init__(self, x, y, vx, vy, ball_type, radius=5):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.ball_type = ball_type
        self.radius = radius
        self.alive = True
        self.bounces = 0
        self.bounces_left = 5

def test_ricochet_mode():
    mode = RicochetMode()
    world = MockWorld()

    # Test bouncing on left wall
    proj1 = MockBall(2, 500, -100, 0, "projectile")
    proj1.bounces = 5
    world.projectiles.append(proj1)

    # Test bouncing on right wall
    proj2 = MockBall(998, 500, 100, 0, "fireball")
    proj2.bounces_left = 0
    world.projectiles.append(proj2)

    # Test bouncing on top wall
    proj3 = MockBall(500, 2, 0, -100, "bullet")
    world.projectiles.append(proj3)

    # Test bouncing on bottom wall
    proj4 = MockBall(500, 998, 0, 100, "snipe")
    world.projectiles.append(proj4)

    mode.tick(world, [], 0.016)

    # Check proj1
    assert proj1.bounces == 0
    assert proj1.bounces_left == 999
    assert proj1.x == 5
    assert proj1.vx == 100

    # Check proj2
    assert proj2.bounces_left == 999
    assert proj2.x == 995
    assert proj2.vx == -100

    # Check proj3
    assert proj3.y == 5
    assert proj3.vy == 100

    # Check proj4
    assert proj4.y == 995
    assert proj4.vy == -100
