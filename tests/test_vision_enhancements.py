import pytest
from src.ai.perception import Perception

class MockArena:
    def __init__(self, is_night=False, is_foggy=False):
        self.is_night = is_night
        self.is_foggy = is_foggy
        self.hazards = []

class MockWorld:
    def __init__(self, arena=None):
        self.arena = arena if arena else MockArena()

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": [], "boosters": [], "traps": []}

class MockEntity:
    def __init__(self, id, x, y, kind=""):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 10
        self.underground = False

class MockBall:
    def __init__(self, x, y, cosmetic=""):
        self.x = x
        self.y = y
        self.cosmetic = cosmetic
        self.has_thermal_vision = False
        self.advanced_optics_active = False

def test_thermal_vision_night():
    passed_radius = []
    class WorldWithCapture(MockWorld):
        def get_nearby_entities(self, ball, radius):
            passed_radius.append(radius)
            return {"enemies": [], "allies": [], "boosters": [], "traps": []}

    arena = MockArena(is_night=True)
    world = WorldWithCapture(arena=arena)

    # Normal ball - perception radius shrinks at night
    ball = MockBall(0, 0)
    ball.perception_radius = 500.0
    perception = Perception(ball, world)
    perception.scan()
    assert passed_radius[0] < 500.0 # Standard night reduction

    passed_radius.clear()

    # Ball with thermal vision - better radius at night
    ball_thermal = MockBall(0, 0, cosmetic="thermal_goggles")
    ball_thermal.perception_radius = 500.0
    perception_thermal = Perception(ball_thermal, world)
    perception_thermal.scan()
    assert passed_radius[0] >= 1000.0 # Boosted by thermal goggles at night

def test_advanced_optics():
    # Will need to mock get_nearby_entities to capture the requested radius
    passed_radius = []

    class WorldWithCapture(MockWorld):
        def get_nearby_entities(self, ball, radius):
            passed_radius.append(radius)
            return {"enemies": [], "allies": [], "boosters": [], "traps": []}

    world = WorldWithCapture()

    ball = MockBall(0, 0)
    ball.advanced_optics_active = True
    ball.perception_radius = 500.0

    perception = Perception(ball, world)
    perception.scan()

    assert passed_radius[0] >= 1500.0

def test_thermal_vision_smoke_bypass():
    passed_radius = []
    class WorldWithCapture(MockWorld):
        def get_nearby_entities(self, ball, radius):
            passed_radius.append(radius)
            return {"enemies": [], "allies": [], "boosters": [], "traps": []}

    arena = MockArena()
    smoke = MockEntity("s1", 0, 0, kind="smokescreen")
    smoke.radius = 20
    arena.hazards.append(smoke)
    world = WorldWithCapture(arena=arena)

    ball = MockBall(0, 0)
    ball.perception_radius = 500.0
    perception = Perception(ball, world)
    perception.scan()

    assert passed_radius[0] <= 50.0 # Smoke reduces radius

    passed_radius.clear()

    ball_thermal = MockBall(0, 0, cosmetic="thermal_goggles")
    ball_thermal.perception_radius = 500.0
    perception_thermal = Perception(ball_thermal, world)
    perception_thermal.scan()

    assert passed_radius[0] == 2000.0 # Thermal gets maxed to 2000.0 due to default day conditions in test
