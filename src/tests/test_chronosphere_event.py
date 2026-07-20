import pytest
import math
from ai.game_modes import ChronosphereEventMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, x=500.0, y=500.0, vx=100.0, vy=100.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.alive = True

        # essential attributes
        self.ball_type = "normal"
        self.max_stamina = 100.0
        self.stamina = 100.0
        self.base_speed = 200.0
        self.speed = 200.0
        self.base_damage = 10.0
        self.original_base_damage = 10.0
        self.traits = []
        self.weather_immunity_timer = 0.0
        self.in_mirror_dimension = False
        self.intangible = False
        self.vision_radius = 200.0
        self.invisible = False

        self.skill_cooldown = 10.0
        self.dash_cooldown = 5.0
        self.attack_cooldown = 2.0

def test_chronosphere_event_inside():
    mode = ChronosphereEventMode()
    world = MockWorld()
    b = MockBall(x=500.0, y=500.0) # exactly at center

    mode.setup(world, [b])

    assert mode.collapse_timer == 20.0

    # Tick inside
    delta = 0.016
    mode.tick(world, [b], delta)

    assert math.isclose(b.skill_cooldown, 10.0 - (delta * 3.0))
    assert math.isclose(b.dash_cooldown, 5.0 - (delta * 3.0))
    assert math.isclose(b.attack_cooldown, 2.0 - (delta * 3.0))

def test_chronosphere_event_outside():
    mode = ChronosphereEventMode()
    world = MockWorld()
    # placed far outside the 300.0 radius (e.g. at 100, 100, dist from 500,500 is ~565 > 300)
    b = MockBall(x=100.0, y=100.0, vx=100.0, vy=100.0)

    mode.setup(world, [b])

    delta = 0.016
    mode.tick(world, [b], delta)

    assert math.isclose(b.x, 100.0 - (100.0 * delta * 0.5))
    assert math.isclose(b.y, 100.0 - (100.0 * delta * 0.5))

    assert math.isclose(b.skill_cooldown, 10.0 + (delta * 0.5))
    assert math.isclose(b.dash_cooldown, 5.0 + (delta * 0.5))
    assert math.isclose(b.attack_cooldown, 2.0 + (delta * 0.5))

def test_chronosphere_collapse():
    mode = ChronosphereEventMode()
    world = MockWorld()
    b = MockBall(x=500.0, y=500.0)

    mode.setup(world, [b])

    # Tick with large delta to collapse
    mode.tick(world, [b], 20.1)

    assert mode.collapse_timer <= 0.0
    # ensure active flag is set to False if it existed
    if mode.hazard_obj:
        assert mode.hazard_obj.active == False
