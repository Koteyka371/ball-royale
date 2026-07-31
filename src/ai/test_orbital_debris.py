import pytest
import math
from ai.game_modes import OrbitalDebrisMutatorMode

class MockBall:
    def __init__(self, id, x, y, vx=0.0, vy=0.0):
        self.id = id
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = 10.0
        self.alive = True
        self.hp = 100.0

class MockProjectile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = True

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.projectiles = []
        self.events = []

    def _deal_damage(self, attacker, target, amount):
        target.hp -= amount
        if target.hp <= 0:
            target.alive = False

def test_orbital_debris_pull():
    mode = OrbitalDebrisMutatorMode()
    world = MockWorld()
    b = MockBall(1, 400.0, 500.0) # Left of center (500, 500)
    mode.setup(world, [b])

    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].kind == "black_hole"

    # pull strength is 200.0
    # dist is 100
    # delta is 0.1
    # b.vx += (100 / 100) * 200 * 0.1 = 20
    mode.tick(world, [b], 0.1)

    assert b.vx > 0.0

def test_orbital_debris_projectile_block():
    mode = OrbitalDebrisMutatorMode()
    world = MockWorld()
    b = MockBall(1, 10.0, 10.0)
    mode.setup(world, [b])

    # Debris positions are based on mode.orbit_angle, which is 0 initially.
    # Center is 500, 500. orbit_radius is 250.
    # 4 debris at angles 0, pi/2, pi, 3pi/2
    # Debris 0: (750, 500)

    # Place a projectile right at (750, 500)
    p = MockProjectile(750.0, 500.0)
    world.projectiles.append(p)

    mode.tick(world, [b], 0.1)

    assert not p.active

def test_orbital_debris_high_speed_collision():
    mode = OrbitalDebrisMutatorMode()
    world = MockWorld()

    # Debris 0: (750, 500). Debris radius is 30, ball radius 10.
    # Let's put ball at 750, 539 moving very fast up
    b = MockBall(1, 750.0, 539.0, vx=0.0, vy=-500.0)
    mode.setup(world, [b])

    initial_hp = b.hp
    mode.tick(world, [b], 0.1)

    # Should collide, bounce, and take damage (speed 500 > 400)
    assert b.hp < initial_hp
    assert b.vy > 0 # bounced

def test_orbital_debris_low_speed_collision():
    mode = OrbitalDebrisMutatorMode()
    world = MockWorld()

    # Debris 0: (750, 500)
    # Let's put ball at 750, 539 moving slowly
    b = MockBall(1, 750.0, 539.0, vx=0.0, vy=-10.0)
    mode.setup(world, [b])

    initial_hp = b.hp
    mode.tick(world, [b], 0.1)

    # Should collide and bounce, but no damage (speed 10 < 400)
    assert b.hp == initial_hp
    assert b.vy > 0 # bounced
