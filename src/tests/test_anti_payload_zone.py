import pytest
import math
from ai.game_modes import EscortMode, DualPayloadMode

class MockBall:
    def __init__(self, id, ball_type, team, x, y):
        self.id = id
        self.ball_type = ball_type
        self.team = team
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 100.0
        self.base_speed = 100.0
        self.alive = True
        self.radius = 15.0
        self.hp = 100.0
        self.max_hp = 100.0

class MockHazard:
    def __init__(self, x, y, radius, kind):
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

def test_escort_mode_anti_payload_zone_slowdown():
    mode = EscortMode()
    world = MockWorld()

    # 2 defenders, 1 attacker
    b1 = MockBall(1, "normal", "Defenders", 100, 500)
    b2 = MockBall(2, "normal", "Defenders", 120, 500) # Close to payload to give speed mult
    b3 = MockBall(3, "normal", "Attackers", 900, 500)
    balls = [b1, b2, b3]

    mode.setup(world, balls)

    # Verify payload was assigned
    assert mode.payload is not None
    mode.payload.speed = 10.0 # Base speed

    # Tick without hazard
    initial_x = mode.payload.x
    mode.tick(world, balls, 1.0)
    dist_moved_normal = mode.payload.x - initial_x

    assert dist_moved_normal > 0

    # Reset position and add hazard
    mode.payload.x = initial_x
    hazard = MockHazard(initial_x, mode.payload.y, 80.0, "anti_payload_zone")
    world.arena.hazards.append(hazard)

    # Tick with hazard
    mode.tick(world, balls, 1.0)
    dist_moved_slowed = mode.payload.x - initial_x

    # Because of float precision and possible multiple ticks, just check it's roughly half (within 5% margin)
    assert dist_moved_slowed > 0
    assert abs(dist_moved_slowed - (dist_moved_normal * 0.5)) < 1.0

def test_dual_payload_mode_anti_payload_zone_slowdown():
    mode = DualPayloadMode()
    world = MockWorld()

    b1 = MockBall(1, "normal", "Red", 100, 500)
    b2 = MockBall(2, "normal", "Red", 120, 500)
    b3 = MockBall(3, "normal", "Blue", 900, 500)
    b4 = MockBall(4, "normal", "Blue", 880, 500)
    balls = [b1, b2, b3, b4]

    mode.setup(world, balls)

    assert mode.payload_red is not None
    assert mode.payload_blue is not None

    mode.payload_red.speed = 10.0
    mode.payload_blue.speed = 10.0

    initial_red_x = mode.payload_red.x
    initial_blue_x = mode.payload_blue.x

    mode.tick(world, balls, 1.0)

    dist_red_normal = mode.payload_red.x - initial_red_x
    dist_blue_normal = initial_blue_x - mode.payload_blue.x # Blue moves left

    mode.payload_red.x = initial_red_x
    mode.payload_blue.x = initial_blue_x

    world.arena.hazards.append(MockHazard(initial_red_x, mode.payload_red.y, 80.0, "anti_payload_zone"))
    world.arena.hazards.append(MockHazard(initial_blue_x, mode.payload_blue.y, 80.0, "anti_payload_zone"))

    mode.tick(world, balls, 1.0)

    dist_red_slowed = mode.payload_red.x - initial_red_x
    dist_blue_slowed = initial_blue_x - mode.payload_blue.x

    assert dist_red_slowed > 0
    assert dist_blue_slowed > 0
    assert abs(dist_red_slowed - (dist_red_normal * 0.5)) < 1.0
    assert abs(dist_blue_slowed - (dist_blue_normal * 0.5)) < 1.0
