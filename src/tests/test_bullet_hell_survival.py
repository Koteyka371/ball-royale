import pytest
from ai.game_modes import BulletHellSurvivalMode

class DummyWorld:
    def __init__(self):
        self.projectiles = []
        self.arena = DummyArena()

class DummyArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class DummyBall:
    def __init__(self):
        self.x = 500.0
        self.y = 500.0
        self.hp = 100.0
        self.alive = True

def test_bullet_hell_survival_mode():
    mode = BulletHellSurvivalMode()
    world = DummyWorld()
    balls = [DummyBall()]

    # Spawn turrets
    for _ in range(800):
        mode.tick(world, balls, delta=0.016)

    assert len(mode.turrets) > 0, "Turrets should be spawned over time"

    # Ensure turrets are invincible and spawn projectiles
    turret = mode.turrets[0]
    assert turret.hp == 999999.0

    # Simulate turret damage
    turret.hp = 10.0
    mode.tick(world, balls, delta=0.016)
    assert turret.hp == 999999.0, "Turrets should instantly recover to max HP"

    assert len(world.projectiles) > 0, "Turrets should fire projectiles"

    # Test projectile bouncing logic
    proj = world.projectiles[0]
    proj.x = -10.0
    proj.y = 500.0
    proj.vx = -100.0
    proj.vy = 0.0

    mode.tick(world, balls, delta=0.016)

    assert proj.vx > 0, "Projectile should bounce off the left wall"
    assert proj.x >= 0, "Projectile should be clamped inside arena"

    proj.x = 500.0
    proj.y = 1010.0
    proj.vx = 0.0
    proj.vy = 100.0

    mode.tick(world, balls, delta=0.016)

    assert proj.vy < 0, "Projectile should bounce off the bottom wall"
    assert proj.y <= 1000, "Projectile should be clamped inside arena"
