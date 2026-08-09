import pytest
from ai.game_modes import DecayingProjectilesMutatorMode

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
    def __init__(self, x, y, vx, vy, radius=10, damage=20, hp=1, alive=True, ball_type="projectile"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.damage = damage
        self.hp = hp
        self.alive = alive
        self.ball_type = ball_type

def test_decaying_projectiles_mutator():
    mode = DecayingProjectilesMutatorMode()
    world = MockWorld()

    proj1 = MockProjectile(1, 100, -100, 0, radius=10, damage=20)
    world.projectiles.append(proj1)

    hazard1 = MockProjectile(1, 100, -100, 0, radius=15, damage=30, ball_type="fireball")
    world.arena.hazards.append(hazard1)

    mode.tick(world, [], 1.0) # 1 second delta

    # Rate is 0.5 decay per sec. New radius = max(1.0, 10 * 0.5) = 5.0
    # ratio = 5.0 / 10 = 0.5. damage = 20 * 0.5 = 10.0

    assert proj1.radius == 5.0
    assert proj1.damage == 10.0
    assert proj1._original_radius == 10
    assert proj1._original_damage == 20

    # Rate is 0.5 decay per sec. New radius = max(1.0, 15 * 0.5) = 7.5
    # ratio = 7.5 / 15 = 0.5. damage = 30 * 0.5 = 15.0

    assert hazard1.radius == 7.5
    assert hazard1.damage == 15.0

    mode.tick(world, [], 1.0)
    # radius is 5.0, decay is 0.5 per sec. max(1.0, 5.0 * 0.5) = 2.5
    # ratio = 2.5 / 10.0 = 0.25. damage = 20 * 0.25 = 5.0

    assert proj1.radius == 2.5
    assert proj1.damage == 5.0
