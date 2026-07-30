import pytest
import math

def test_orbital_debris_high_speed_collision():
    from ai.game_modes import GAME_MODES
    mode = GAME_MODES["orbital_debris"]

    class Arena:
        def __init__(self):
            self.width = 1000.0
            self.height = 1000.0
            self.hazards = []

    class World:
        def __init__(self):
            self.arena = Arena()
            self.projectiles = []

    class Ball:
        def __init__(self, x, y, vx, vy):
            self.alive = True
            self.hp = 100.0
            self.x = x
            self.y = y
            self.vx = vx
            self.vy = vy
            self.radius = 10.0

    world = World()
    balls = []
    mode.setup(world, balls)

    # Get first debris
    debris = next(h for h in world.arena.hazards if getattr(h, "kind", "") == "orbital_debris")

    # Create ball colliding with it at high speed
    # Debris radius is 40, ball is 10. Distance must be < 50
    # Let's place it at distance 45
    b = Ball(debris.x + 45.0, debris.y, -300.0, 0.0)
    balls.append(b)

    mode.tick(world, balls, 0.016)

    # High speed collision (speed > 200) should reduce HP
    assert b.hp < 100.0

    # Should have bounced
    assert b.vx > 0.0

def test_orbital_debris_low_speed_collision():
    from ai.game_modes import GAME_MODES
    mode = GAME_MODES["orbital_debris"]

    class Arena:
        def __init__(self):
            self.width = 1000.0
            self.height = 1000.0
            self.hazards = []

    class World:
        def __init__(self):
            self.arena = Arena()
            self.projectiles = []

    class Ball:
        def __init__(self, x, y, vx, vy):
            self.alive = True
            self.hp = 100.0
            self.x = x
            self.y = y
            self.vx = vx
            self.vy = vy
            self.radius = 10.0

    world = World()
    balls = []
    mode.setup(world, balls)

    # Get first debris
    debris = next(h for h in world.arena.hazards if getattr(h, "kind", "") == "orbital_debris")

    # Low speed (100)
    b = Ball(debris.x + 45.0, debris.y, -100.0, 0.0)
    balls.append(b)

    mode.tick(world, balls, 0.016)

    # No damage for low speed
    assert b.hp == 100.0

    # Still bounces
    assert b.vx > 0.0
