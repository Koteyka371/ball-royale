import pytest
from ai.game_modes import BouncingProjectilesMutatorMode

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

def test_bouncing_projectiles_mutator():
    mode = BouncingProjectilesMutatorMode()
    world = MockWorld()

    proj1 = MockProjectile(1, 100, -100, 0)
    world.projectiles.append(proj1)

    # Tick 1: Proj1 should bounce off left wall
    mode.tick(world, [], 0.016)
    assert proj1.vx == 100
    assert getattr(proj1, "bounces", 0) == 1

    # Proj1 now moving right. Put it near right wall.
    proj1.x = 999
    mode.tick(world, [], 0.016)
    assert proj1.vx == -100
    assert getattr(proj1, "bounces", 0) == 2

    # Proj1 now moving left. Put it near left wall.
    proj1.x = 1
    mode.tick(world, [], 0.016)
    assert proj1.vx == 100
    assert getattr(proj1, "bounces", 0) == 3

    # Proj1 bounces is 3. Put near right wall. It should dissipate.
    proj1.x = 999
    mode.tick(world, [], 0.016)
    assert not proj1.alive
    assert proj1.hp == 0

def test_hazard_bouncing():
    mode = BouncingProjectilesMutatorMode()
    world = MockWorld()

    proj = MockProjectile(100, 100, 100, 0)
    world.projectiles.append(proj)

    hazard = MockProjectile(105, 100, 0, 0, radius=5, ball_type="hazard")
    world.arena.hazards.append(hazard)

    mode.tick(world, [], 0.016)

    assert proj.vx < 0
    assert getattr(proj, "bounces", 0) == 1
