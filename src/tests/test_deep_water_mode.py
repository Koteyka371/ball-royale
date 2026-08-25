import pytest
import math
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id_val, x, y):
        self.id = id_val
        self.x = x
        self.y = y
        self.alive = True
        self.ball_type = "normal"
        self.traits = []
        self.radius = 10.0
        self.base_speed = 100.0
        self.speed = 100.0
        self.base_max_speed = 100.0
        self.max_speed = 100.0
        self.base_perception_radius = 200.0
        self.perception_radius = 200.0
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.buoyant_buff_timer = 0.0

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockHazard:
    def __init__(self, kind, x, y, radius, life):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.life = life

def test_deep_water_slowdown():
    mode = GAME_MODES["deep_water"]
    world = MockWorld()
    b1 = MockBall(1, 100, 100) # non-aquatic
    b2 = MockBall(2, 200, 200) # aquatic
    b2.traits.append("aquatic")

    balls = [b1, b2]
    mode.setup(world, balls)

    # Do tick without hazards to check slowdown
    mode.tick(world, balls, delta=1.0)

    assert abs(b1.speed - b1.base_speed * 0.5) < 0.1
    assert abs(b1.perception_radius - 100.0) < 0.1

    assert abs(b2.speed - b2.base_speed) < 0.1
    assert abs(b2.perception_radius - 200.0) < 0.1

def test_whirlpool_pull():
    mode = GAME_MODES["deep_water"]
    world = MockWorld()
    b1 = MockBall(1, 100, 100)

    balls = [b1]
    mode.setup(world, balls)

    # Manually add whirlpool at 150, 150
    whirlpool = MockHazard("giant_whirlpool", 150, 150, 200.0, 10.0)
    world.arena.hazards.append(whirlpool)

    # Save original position
    orig_x = b1.x
    orig_y = b1.y

    mode.tick(world, balls, delta=1.0)

    # Should move towards 150, 150
    assert b1.x > orig_x
    assert b1.y > orig_y

def test_debris_buff():
    mode = GAME_MODES["deep_water"]
    world = MockWorld()
    b1 = MockBall(1, 100, 100)
    b1.stamina = 50.0

    balls = [b1]
    mode.setup(world, balls)

    # Manually add debris at 100, 100
    debris = MockHazard("floating_debris", 100, 100, 40.0, 10.0)
    world.arena.hazards.append(debris)

    mode.tick(world, balls, delta=1.0)

    # Should have normal speed, buff timer active, and stamina increased
    assert b1.buoyant_buff_timer > 0.0
    assert abs(b1.speed - b1.base_speed) < 0.1
    assert abs(b1.perception_radius - 200.0) < 0.1
    assert b1.stamina > 50.0
