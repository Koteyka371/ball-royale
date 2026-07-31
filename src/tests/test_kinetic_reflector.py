import pytest
from ai.game_modes import GameMode

class MockHazard:
    def __init__(self, kind, x, y, radius=50.0):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius

class MockBall:
    def __init__(self, id, x, y, vx, vy, radius=15.0):
        self.id = id
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.alive = True
        self.ball_type = "normal"

class MockProjectile:
    def __init__(self, id, x, y, vx, vy, radius=5.0, damage=10.0):
        self.id = id
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.damage = damage

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.projectiles = []

    def add_event(self, type, data):
        self.events.append({"type": type, "data": data})

def test_kinetic_reflector():
    world = MockWorld()
    hazard = MockHazard("kinetic_reflector", 100.0, 100.0, 50.0)
    world.arena.hazards.append(hazard)

    # Ball inside
    ball1 = MockBall(1, 100.0, 100.0, 10.0, 5.0)
    # Ball outside
    ball2 = MockBall(2, 300.0, 300.0, -10.0, -5.0)

    # Projectile inside
    proj1 = MockProjectile(3, 100.0, 100.0, 20.0, 0.0)
    # Projectile outside
    proj2 = MockProjectile(4, 400.0, 400.0, 0.0, 20.0)

    world.projectiles.append(proj1)
    world.projectiles.append(proj2)

    balls = [ball1, ball2]

    mode = GameMode()

    import random
    random.seed(42) # For predictable multipliers, though testing exact output might be flaky, we test sign

    # Store initial velocity directions
    b1_vx_orig, b1_vy_orig = ball1.vx, ball1.vy
    p1_vx_orig, p1_damage_orig = proj1.vx, proj1.damage

    mode.apply_dynamic_traits(world, balls, 0.016)

    # Ball 1 should have its velocity flipped and scaled
    assert ball1.vx * b1_vx_orig < 0 # Sign changed
    assert ball1.vy * b1_vy_orig < 0

    # Projectile 1 should have velocity flipped and damage increased
    assert proj1.vx * p1_vx_orig < 0
    assert proj1.damage != p1_damage_orig # Random multiplier applied

    # Ball 2 and Projectile 2 should be unaffected
    assert ball2.vx == -10.0
    assert ball2.vy == -5.0
    assert proj2.vx == 0.0
    assert proj2.vy == 20.0

    # Check that an event was generated
    assert len(world.events) == 2 # one for ball, one for projectile
    assert world.events[0]["type"] == "kinetic_reflection"

    # Run again, ball 1 shouldn't flip again because it's still inside
    b1_vx_new = ball1.vx
    p1_vx_new = proj1.vx
    mode.apply_dynamic_traits(world, balls, 0.016)
    assert ball1.vx == b1_vx_new
    assert proj1.vx == p1_vx_new

    # Move ball 1 outside
    ball1.x = 200.0
    mode.apply_dynamic_traits(world, balls, 0.016)

    # Move it back inside
    ball1.x = 100.0
    mode.apply_dynamic_traits(world, balls, 0.016)

    # It should flip again
    assert ball1.vx * b1_vx_new < 0
