import pytest
from ai.game_modes import LaserMirrorBordersMode

class MockArena:
    def __init__(self, width, height):
        self.width = width
        self.height = height

class MockProjectile:
    def __init__(self, x, y, vx, vy, bounces_left=0, damage=10.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = 10.0
        self.bounces_left = bounces_left
        self.damage = damage
        self.alive = True
        self.hp = 1.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena(1000, 1000)
        self.projectiles = []

def test_laser_mirror_borders_mode():
    mode = LaserMirrorBordersMode()
    world = MockWorld()

    # Left border hit
    proj_left = MockProjectile(-5, 500, -100, 0, bounces_left=1, damage=10.0)
    # Right border hit
    proj_right = MockProjectile(1005, 500, 100, 0, bounces_left=1, damage=10.0)
    # Top border hit
    proj_top = MockProjectile(500, -5, 0, -100, bounces_left=1, damage=10.0)
    # Bottom border hit
    proj_bottom = MockProjectile(500, 1005, 0, 100, bounces_left=1, damage=10.0)

    # Normal projectile inside arena
    proj_normal = MockProjectile(500, 500, 100, 100, bounces_left=1, damage=10.0)

    world.projectiles = [proj_left, proj_right, proj_top, proj_bottom, proj_normal]

    mode.tick(world, [], 1.0)

    assert proj_left.vx == 100
    assert proj_left.x == 10.0
    assert proj_left.bounces_left == 2
    assert proj_left.damage == 12.5

    assert proj_right.vx == -100
    assert proj_right.x == 990.0
    assert proj_right.bounces_left == 2
    assert proj_right.damage == 12.5

    assert proj_top.vy == 100
    assert proj_top.y == 10.0
    assert proj_top.bounces_left == 2
    assert proj_top.damage == 12.5

    assert proj_bottom.vy == -100
    assert proj_bottom.y == 990.0
    assert proj_bottom.bounces_left == 2
    assert proj_bottom.damage == 12.5

    assert proj_normal.vx == 100
    assert proj_normal.vy == 100
    assert proj_normal.x == 500
    assert proj_normal.y == 500
    assert proj_normal.bounces_left == 1
    assert proj_normal.damage == 10.0
