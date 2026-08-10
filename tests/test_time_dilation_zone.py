import sys
import pytest
sys.path.insert(0, ".")
from src.ai.game_modes import TimeDilationZoneMode

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.projectiles = []

class MockBall:
    def __init__(self):
        self.alive = True
        self.x = 500
        self.y = 500
        self.vx = 100
        self.vy = 0
        self.skill_timer = 2.0
        self.dash_cooldown = 2.0

class MockHazard:
    def __init__(self):
        self.active = True
        self.x = 500
        self.y = 500
        self.vx = 100
        self.vy = 0
        self.explosion_timer = 2.0

class MockProjectile:
    def __init__(self):
        self.active = True
        self.x = 500
        self.y = 500
        self.vx = 100
        self.vy = 0
        self.duration = 2.0

def test_time_dilation_zone():
    world = MockWorld()
    hazard = MockHazard()
    proj = MockProjectile()
    ball = MockBall()
    world.arena.hazards.append(hazard)
    world.projectiles.append(proj)

    mode = TimeDilationZoneMode()
    mode.setup(world, [ball])

    mode.tick(world, [ball], 0.5)

    assert ball.x == 475.0, f"Ball x was {ball.x}"
    assert ball.dash_cooldown == 2.25, f"Ball cooldown was {ball.dash_cooldown}"
    assert hazard.x == 475.0, f"Hazard x was {hazard.x}"
    assert hazard.explosion_timer == 2.25, f"Hazard timer was {hazard.explosion_timer}"
    assert proj.x == 475.0, f"Proj x was {proj.x}"
    assert proj.duration == 2.25, f"Proj duration was {proj.duration}"
