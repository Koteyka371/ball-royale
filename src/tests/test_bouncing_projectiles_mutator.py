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

class MockProj:
    def __init__(self, x, y, vx, vy, kind):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.kind = kind
        self.alive = True
        self.hp = 1.0
        self.radius = 5.0
        self.bounces = 0
        self.bounces_left = 1

def test_bouncing_projectiles_mutator():
    world = MockWorld()
    mode = BouncingProjectilesMutatorMode()

    # Left wall collision
    proj_left = MockProj(2, 500, -100, 0, "projectile")
    world.projectiles.append(proj_left)

    # Right wall collision
    proj_right = MockProj(998, 500, 100, 0, "projectile")
    world.projectiles.append(proj_right)

    # Top wall collision
    proj_top = MockProj(500, 2, 0, -100, "projectile")
    world.projectiles.append(proj_top)

    # Bottom wall collision
    proj_bottom = MockProj(500, 998, 0, 100, "projectile")
    world.projectiles.append(proj_bottom)

    # Hazard collision
    hazard = MockProj(500, 500, 0, 0, "hazard")
    hazard.radius = 10.0
    world.arena.hazards.append(hazard)

    proj_hazard = MockProj(486, 500, 100, 0, "projectile")
    world.projectiles.append(proj_hazard)

    mode.tick(world, [], 0.016)

    assert proj_left.vx == 100
    assert proj_left.x == 5.0
    assert proj_left.bounces_left == 2
    assert proj_left.bounces == 1

    assert proj_right.vx == -100
    assert proj_right.x == 995.0
    assert proj_right.bounces_left == 2
    assert proj_right.bounces == 1

    assert proj_top.vy == 100
    assert proj_top.y == 5.0
    assert proj_top.bounces_left == 2
    assert proj_top.bounces == 1

    assert proj_bottom.vy == -100
    assert proj_bottom.y == 995.0
    assert proj_bottom.bounces_left == 2
    assert proj_bottom.bounces == 1

    # Hazard bounce
    assert proj_hazard.vx == -100.0  # Reflected completely on x-axis
    assert proj_hazard.bounces_left == 2
    assert proj_hazard.bounces == 1
    print(f"Proj hazard x: {proj_hazard.x}, y: {proj_hazard.y}, vx: {proj_hazard.vx}, vy: {proj_hazard.vy}")
