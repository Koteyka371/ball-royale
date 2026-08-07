import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.projectiles = []

    def add_event(self, kind, data):
        self.events.append({"type": kind, **data})

class MockBall:
    def __init__(self, x=500.0, y=500.0, vx=0.0, vy=0.0, ball_type="normal", alive=True):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.ball_type = ball_type
        self.alive = alive

class MockProjectile:
    def __init__(self, x=500.0, y=500.0, vx=0.0, vy=0.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

def test_orbital_black_hole_event_spawn():
    mode = GAME_MODES["orbital_black_hole_event"]
    mode.active = False
    world = MockWorld()

    # Force activation
    while not mode.active:
        mode.tick(world, [], delta=100.0) # High delta to force random trigger

    assert mode.active is True
    assert mode.timer == 15.0
    assert any(e["type"] == "orbital_black_hole" for e in world.events)

def test_orbital_black_hole_pulls_balls_and_boosts_tangential():
    mode = GAME_MODES["orbital_black_hole_event"]
    mode.active = True
    mode.timer = 10.0

    world = MockWorld()

    # Place a ball at (400, 500), moving purely right (vx=100)
    # Center is (500, 500)
    # dx = 100, dy = 0. Tangent is (0, 1) or (0, -1).
    # Since ball velocity is (100, 0), dot product with (0, 1) and (0, -1) are both 0.
    # It will pick one tangential direction. Let's make it have a slight tangent velocity so it picks it predictably.
    ball = MockBall(x=400.0, y=500.0, vx=0.0, vy=100.0)

    initial_x = ball.x
    initial_y = ball.y
    initial_vx = ball.vx
    initial_vy = ball.vy

    delta = 1.0
    mode.tick(world, [ball], delta)

    # Check pull: dx = 100, dy = 0
    # pull_strength = 50.0
    # b.x += (100/100) * 50.0 * 1.0 = 50.0
    assert ball.x > initial_x # pulled towards center (500, 500)
    assert ball.x == initial_x + 50.0

    # Check tangential boost: tangent_x = 0, tangent_y = 1
    # tangential_boost = 150.0
    # b.y += 1 * 150.0 * 1.0 = 150.0
    assert ball.y > initial_y
    assert ball.y == initial_y + 150.0

def test_orbital_black_hole_pulls_projectiles_heavily():
    mode = GAME_MODES["orbital_black_hole_event"]
    mode.active = True
    mode.timer = 10.0

    world = MockWorld()
    proj = MockProjectile(x=400.0, y=500.0, vx=10.0, vy=0.0)
    world.projectiles.append(proj)

    delta = 1.0
    mode.tick(world, [], delta)

    # Center is (500, 500), dx = 100, dy = 0
    # Projectile pull is 500.0
    # proj.vx += (100/100) * 500.0 * 1.0 = 500.0
    assert proj.vx == 10.0 + 500.0
    assert proj.vy == 0.0
