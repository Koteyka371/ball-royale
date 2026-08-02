import pytest
from ai.game_modes import FrictionZonesMode
from ai.action import Action

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 500
        self.y = 500
        self.vx = 0.0
        self.vy = 0.0
        self.mass = 1.0
        self.alive = True
        self.ball_type = "player"

def test_friction_zones_spawn():
    mode = FrictionZonesMode()
    world = MockWorld()
    balls = [MockBall()]
    mode.setup(world, balls)

    # Tick to spawn zone
    mode.tick(world, balls, delta=5.1)

    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert hazard.kind in ["ice_zone", "mud_zone"]

def test_friction_zones_effect():
    mode = FrictionZonesMode()
    world = MockWorld()
    ball = MockBall()
    balls = [ball]
    mode.setup(world, balls)

    # create ice zone
    class MockHazard:
        def __init__(self):
            self.x = 500
            self.y = 500
            self.radius = 150
            self.kind = "ice_zone"
            self.zone_type = "ice"
            self.duration = 10

    h = MockHazard()
    world.arena.hazards.append(h)

    mode.tick(world, balls, delta=0.1)
    assert getattr(ball, "is_frictionless", False) == True
    assert getattr(ball, "friction_multiplier", 1.0) == 0.1

    # change to mud
    h.kind = "mud_zone"
    h.zone_type = "mud"

    mode.tick(world, balls, delta=0.1)
    assert getattr(ball, "is_frictionless", False) == False
    assert getattr(ball, "friction_multiplier", 1.0) == 3.0
