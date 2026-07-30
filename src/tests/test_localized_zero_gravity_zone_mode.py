import pytest
from ai.game_modes import LocalizedZeroGravityZoneMode

class DummyArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class DummyWorld:
    def __init__(self):
        self.arena = DummyArena()

class DummyBall:
    def __init__(self):
        self.id = 1
        self.alive = True
        self.ball_type = "player"
        self.x = 500
        self.y = 500
        self.radius = 15.0
        self.base_speed = 100.0
        self.speed = 100.0
        self.is_frictionless = False
        self.friction_multiplier = 1.0

def test_localized_zero_gravity_zone_mode_spawns_and_applies():
    world = DummyWorld()
    mode = LocalizedZeroGravityZoneMode()
    balls = [DummyBall()]

    # Fast forward timer to spawn hazard
    mode.tick(world, balls, 5.1)
    assert len(world.arena.hazards) == 1

    zone = world.arena.hazards[0]
    zone_dict = zone if isinstance(zone, dict) else vars(zone)
    assert zone_dict["kind"] == "zero_gravity_zone"
    assert zone_dict["active"] == True

    # Place ball inside the zone
    balls[0].x = zone_dict["x"]
    balls[0].y = zone_dict["y"]

    mode.tick(world, balls, 0.1)

    # Effect should be applied
    assert balls[0].is_frictionless == True
    assert balls[0].friction_multiplier == 0.0
    assert balls[0].speed == 300.0
    assert getattr(balls[0], "zero_g_speed_applied", False) == True

    # Move ball out of zone
    balls[0].x = zone_dict["x"] + 1000.0

    mode.tick(world, balls, 0.1)

    # Effect should be removed
    assert balls[0].is_frictionless == False
    assert balls[0].friction_multiplier == 1.0
    assert balls[0].speed == 100.0
    assert getattr(balls[0], "zero_g_speed_applied", False) == False
