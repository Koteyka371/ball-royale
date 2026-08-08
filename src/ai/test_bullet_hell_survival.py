import pytest
from ai.game_modes import BulletHellSurvivalMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.projectiles = []
        self.events = []

class MockBall:
    def __init__(self, id_val, x, y, team):
        self.id = id_val
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.hp = 100.0

def test_bullet_hell_survival_turret_spawning():
    mode = BulletHellSurvivalMode()
    world = MockWorld()
    balls = [MockBall(1, 500, 500, "Team A")]

    # Fast forward to trigger turret spawn
    mode.spawn_timer = mode.spawn_interval
    mode.tick(world, balls, 0.1)

    assert len(mode.turrets) == 1
    t = mode.turrets[0]
    assert t.kind == "invincible_turret"
    assert t.hp == 999999.0
    assert t in world.arena.hazards

def test_bullet_hell_survival_projectile_generation():
    mode = BulletHellSurvivalMode()
    world = MockWorld()

    t = mode._InvincibleTurret(1, 500, 500)
    mode.turrets.append(t)

    # Fast forward to trigger turret fire
    t.fire_timer = mode.turret_fire_interval
    mode.tick(world, [], 0.1)

    assert len(world.projectiles) == 1
    proj = world.projectiles[0]
    assert proj.kind == "projectile"
    assert proj.team == "Turrets"
    assert proj.damage == t.damage

def test_bullet_hell_survival_boundary_bouncing():
    mode = BulletHellSurvivalMode()
    world = MockWorld()

    # Place a projectile out of bounds on the left moving left
    proj = mode._BouncingProjectile(1, -10, 500, -100, 0, 10, 15)
    world.projectiles.append(proj)

    mode.tick(world, [], 0.1)

    assert proj.x == 10
    assert proj.vx == 100

    # Place a projectile out of bounds on the right moving right
    proj2 = mode._BouncingProjectile(2, 1010, 500, 100, 0, 10, 15)
    world.projectiles.append(proj2)

    mode.tick(world, [], 0.1)

    assert proj2.x == 990
    assert proj2.vx == -100

    # Place a projectile out of bounds on top moving up
    proj3 = mode._BouncingProjectile(3, 500, -10, 0, -100, 10, 15)
    world.projectiles.append(proj3)

    mode.tick(world, [], 0.1)

    assert proj3.y == 10
    assert proj3.vy == 100

    # Place a projectile out of bounds on bottom moving down
    proj4 = mode._BouncingProjectile(4, 500, 1010, 0, 100, 10, 15)
    world.projectiles.append(proj4)

    mode.tick(world, [], 0.1)

    assert proj4.y == 990
    assert proj4.vy == -100
