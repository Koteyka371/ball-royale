import sys
sys.path.append('src')

from ai.game_modes import GAME_MODES

class MockHazard:
    def __init__(self, kind, radius):
        self.kind = kind
        self.radius = radius
        self.original_radius = radius

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = [MockHazard("water", 20.0), MockHazard("rock", 15.0)]

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, type, data):
        self.events.append((type, data))

class MockBall:
    def __init__(self):
        self.base_speed = 100.0
        self.speed = 100.0
        self.base_perception_radius = 150.0
        self.perception_radius = 150.0
        self.alive = True
        self.hp = 100.0

def test_monsoon_weather_reduces_visibility_and_speed():
    mode = GAME_MODES["extreme_weather"]
    world = MockWorld()
    b1 = MockBall()
    mode.setup(world, [b1])

    mode.current_weather = "monsoon"
    mode.tick(world, [b1], 1.0)

    assert b1.perception_radius == 150.0 * 0.4
    assert b1.speed == 120.0 * 0.75

def test_monsoon_weather_expands_water():
    mode = GAME_MODES["extreme_weather"]
    world = MockWorld()
    b1 = MockBall()
    mode.setup(world, [b1])

    mode.current_weather = "monsoon"
    mode.tick(world, [b1], 1.0)

    water_hazard = next(h for h in world.arena.hazards if h.kind == "water")
    assert water_hazard.radius == 40.0

def test_monsoon_weather_shrinks_water_when_over():
    mode = GAME_MODES["extreme_weather"]
    world = MockWorld()
    b1 = MockBall()
    mode.setup(world, [b1])

    mode.current_weather = "monsoon"
    mode.tick(world, [b1], 1.0)

    mode.current_weather = "clear"
    mode.tick(world, [b1], 1.0)

    water_hazard = next(h for h in world.arena.hazards if h.kind == "water")
    assert water_hazard.radius == 30.0

def test_monsoon_weather_spawns_mud_puddles():
    mode = GAME_MODES["extreme_weather"]
    world = MockWorld()
    b1 = MockBall()
    mode.setup(world, [b1])

    mode.current_weather = "monsoon"
    mode.random.seed(42) # Try to ensure spawn

    for _ in range(100):
        mode.tick(world, [b1], 0.1)

    mud_puddles = [h for h in world.arena.hazards if getattr(h, "kind", "") == "mud_puddle"]
    assert len(mud_puddles) > 0
