import pytest
from ai.game_modes import HealthyGravityWellMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, x, y, hp=100.0):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.hp = hp
        self.alive = True
        self.ball_type = "player"

def test_healthy_gravity_well_pulls_high_hp():
    world = MockWorld()
    mode = HealthyGravityWellMode()
    b1 = MockBall(500, 400, hp=100) # Should be pulled (hp > 75)
    b2 = MockBall(500, 400, hp=50)  # Should NOT be pulled (hp <= 75)

    balls = [b1, b2]
    mode.setup(world, balls)

    # Verify hazard exists
    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].kind == "healthy_gravity_well"

    mode.tick(world, balls, 1.0)

    # b1 is at (500, 400), center is (500, 500)
    # distance is 100
    # pull strength = base / dist^2 = 5000000 / 10000 = 500
    # dy = cy - b1.y = 100, dx = 0
    # vy += (dy/dist) * pull * delta = (100/100) * 500 * 1.0 = 500
    assert b1.vy > 400.0
    assert b1.vx == 0.0

    # b2 should be untouched
    assert b2.vy == 0.0
    assert b2.vx == 0.0

def test_healthy_gravity_well_damage():
    world = MockWorld()
    mode = HealthyGravityWellMode()
    b1 = MockBall(500, 480, hp=100) # Inside horizon (radius 50)
    balls = [b1]
    mode.setup(world, balls)
    mode.tick(world, balls, 1.0)

    # Should take damage
    assert b1.hp < 100
    assert b1.hp == 75.0 # hp - 25*1.0
