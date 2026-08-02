import pytest
from ai.game_modes import FrictionZonesMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.tick = 0

class MockBall:
    def __init__(self, x, y):
        self.id = 1
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 15.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.ball_type = "normal"
        self.friction_multiplier = 1.0
        self.is_frictionless = False

def test_friction_zones():
    mode = FrictionZonesMode()
    world = MockWorld()
    ball = MockBall(500, 500)
    balls = [ball]

    mode.setup(world, balls)

    # Tick to spawn a zone
    for _ in range(6):
        mode.tick(world, balls, delta=1.0)

    assert len(world.arena.hazards) > 0
    hazard = world.arena.hazards[0]

    # Move ball into hazard
    ball.x = hazard.x
    ball.y = hazard.y

    mode.tick(world, balls, delta=1.0)

    if hazard.zone_type == "ice":
        assert ball.friction_multiplier == 0.0
        assert ball.is_frictionless == True
    elif hazard.zone_type == "mud":
        assert ball.friction_multiplier == 3.0

    # Move ball out of hazard
    ball.x = hazard.x + 200
    ball.y = hazard.y

    mode.tick(world, balls, delta=1.0)

    assert ball.friction_multiplier == 1.0
    assert ball.is_frictionless == False
