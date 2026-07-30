import pytest
import math

def test_orbital_debris_projectile_blocking():
    from ai.game_modes import GAME_MODES
    mode = GAME_MODES["orbital_debris"]

    class Arena:
        def __init__(self):
            self.width = 1000.0
            self.height = 1000.0
            self.hazards = []

    class Projectile:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.kind = "projectile"

    class World:
        def __init__(self):
            self.arena = Arena()
            self.projectiles = []

    world = World()
    balls = []
    mode.setup(world, balls)

    # Let's get the coordinates of the first orbital debris
    debris = next(h for h in world.arena.hazards if getattr(h, "kind", "") == "orbital_debris")

    # Create a projectile right on top of it
    p = Projectile(debris.x, debris.y)
    world.projectiles.append(p)

    assert len(world.projectiles) == 1

    mode.tick(world, balls, 0.016)

    # Projectile should be blocked/removed
    assert len(world.projectiles) == 0
