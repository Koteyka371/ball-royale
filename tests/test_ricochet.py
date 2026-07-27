import pytest
from ai.game_modes import GAME_MODES

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

def test_ricochet_mode():
    mode = GAME_MODES['ricochet']
    world = MockWorld()

    proj1 = MockProjectile(1, 100, -100, 0)
    world.projectiles.append(proj1)

    proj1.bounces_left = 1

    # Tick 1: Bounces off left wall
    mode.tick(world, [])
    assert proj1.vx == 100
    assert proj1.x == 5
    assert proj1.bounces_left == 9999

    # Move to right wall
    proj1.x = 999
    proj1.vx = 100

    # Tick 2: Bounces off right wall
    mode.tick(world, [])
    assert proj1.vx == -100
    assert proj1.x == 995
    assert proj1.bounces_left == 9999
