import pytest
from ai.game_modes import LaserMirrorsMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.projectiles = []

class MockProjectile:
    def __init__(self, x, y, vx, vy, radius=5, hp=1, alive=True, ball_type="projectile"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.hp = hp
        self.alive = alive
        self.ball_type = ball_type
        self.damage = 10.0
        self.speed = 100.0

def test_laser_mirrors_mode():
    mode = LaserMirrorsMode()
    world = MockWorld()

    proj1 = MockProjectile(1, 100, -100, 0)
    world.projectiles.append(proj1)

    # Tick 1: Proj1 should bounce off left wall
    mode.tick(world, [], 0.016)
    assert abs(proj1.vx - 110.0) < 0.001
    assert getattr(proj1, "bounces", 0) == 1
    assert abs(proj1.damage - 12.5) < 0.001
    assert abs(proj1.speed - 110.0) < 0.001

    # Proj1 now moving right. Put it near right wall.
    proj1.x = 999
    mode.tick(world, [], 0.016)
    assert abs(proj1.vx + 121.0) < 0.001
    assert getattr(proj1, "bounces", 0) == 2
    assert abs(proj1.damage - 15.625) < 0.001
    assert abs(proj1.speed - 121.0) < 0.001

def test_hazard_laser_mirrors():
    mode = LaserMirrorsMode()
    world = MockWorld()

    # Hazard is a projectile-like hazard
    hazard = MockProjectile(1, 500, -50, 0, radius=5, ball_type="laser_beam")
    world.arena.hazards.append(hazard)

    mode.tick(world, [], 0.016)

    assert abs(hazard.vx - 55.0) < 0.001
    assert getattr(hazard, "bounces", 0) == 1
    assert abs(hazard.damage - 12.5) < 0.001
