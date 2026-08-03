import pytest
import math

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, t, x, y):
        self.ball_type = t
        self.x = x
        self.y = y
        self.alive = True
        self.hp = 100.0
        self.max_hp = 100.0
        self.perception_radius = 250.0
        self.base_perception_radius = 250.0
        self.speed_multiplier = 1.0

def test_solar_radiation_storm_mechanics():
    from ai.game_modes import SolarRadiationStormMode
    mode = SolarRadiationStormMode()
    world = MockWorld()

    # Out in the open
    b1 = MockBall("scout", 100, 100)
    # Solar bot out in the open
    b2 = MockBall("solar_bot", 200, 200)

    balls = [b1, b2]
    mode.setup(world, balls)

    assert not mode.is_flaring
    assert len(mode.solar_walls) == 5

    # Trigger flare
    mode.tick(world, balls, 20.0)
    assert mode.is_flaring

    # Tick during flare
    mode.tick(world, balls, 1.0)

    # b1 (scout) should take damage and be blinded
    assert b1.hp < 100.0
    assert b1.perception_radius == b1.base_perception_radius * 0.2
    assert b1.solar_blinded

    # b2 (solar bot) should get buffed
    assert b2.hp == 100.0 # Healed but capped
    assert b2.speed_multiplier == 2.0

    # End flare
    mode.tick(world, balls, 5.0)
    assert not mode.is_flaring

    # b1 vision restored
    assert b1.perception_radius == b1.base_perception_radius
    assert not getattr(b1, "solar_blinded", False)

def test_solar_radiation_storm_cover():
    from ai.game_modes import SolarRadiationStormMode
    mode = SolarRadiationStormMode()
    world = MockWorld()

    mode.setup(world, [])

    # We will manually place a wall and put a ball right behind it relative to the sun.
    mode.solar_walls = []

    wall = type('Wall', (object,), {
        'x': 500,
        'y': 500,
        'width': 200,
        'height': 50,
        'angle': 0,
        'destructible': False,
        'hp': 999999,
        'max_hp': 999999,
        'is_solar_shield': True,
        'kind': 'indestructible_wall'
    })()
    mode.solar_walls.append(wall)

    # Sun vector is approx (0.707, 0.707) in Python code
    # We want dot product > 0 and < 200, and perp_dist < 50.

    b1 = MockBall("scout", 550, 550) # Should be in cover
    b2 = MockBall("scout", 200, 200) # Should be exposed

    balls = [b1, b2]

    # Trigger flare
    mode.is_flaring = True

    # Tick during flare
    mode.tick(world, balls, 1.0)

    # b1 (in cover) should NOT take damage and NOT be blinded
    assert b1.hp == 100.0
    assert not getattr(b1, "solar_blinded", False)
    assert b1.perception_radius == b1.base_perception_radius

    # b2 (exposed) should take damage and be blinded
    assert b2.hp < 100.0
    assert getattr(b2, "solar_blinded", False)
    assert b2.perception_radius < b2.base_perception_radius
