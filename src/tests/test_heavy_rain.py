from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.name = "default"
        self.weather = "clear"
        self.is_raining = False
        self.hazards = []
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []
        self.events = []

    def add_event(self, type, data):
        self.events.append((type, data))

class MockBall:
    def __init__(self, id, ball_type="base", hp=100.0, speed=100.0, traits=None):
        self.id = id
        self.alive = True
        self.ball_type = ball_type
        self.hp = hp
        self.max_hp = 100.0
        self.speed = speed
        self.base_speed = speed
        self.damage = 10.0
        self.base_damage = 10.0
        self.traits = traits or []
        self.vx = 0.0
        self.vy = 0.0
        self.x = 0.0
        self.y = 0.0
        self.weather_immunity_timer = 0.0

class MockHazard:
    def __init__(self, kind, radius):
        self.kind = kind
        self.radius = radius

def test_heavy_rain_mutator():
    mode = GAME_MODES["heavy_rain_mutator"]
    world = MockWorld()

    b1 = MockBall(1, "base", 100.0)
    b2 = MockBall(2, "water_elemental", 100.0) # Water type

    balls = [b1, b2]

    mode.setup(world, balls)

    assert world.arena.weather == "heavy_rain"
    assert world.arena.is_raining == True

    # Add some hazards
    h1 = MockHazard("rock", 15.0) # Small rock
    h2 = MockHazard("rock", 30.0) # Big rock
    world.arena.hazards = [h1, h2]

    # Tick for 10 seconds to trigger hazard destroy
    for _ in range(10):
        mode.tick(world, balls, 1.0)

    # Check DoT
    # b1 (non-water) should lose 5 hp per sec * 10 sec = 50 hp
    assert b1.hp == 50.0

    # b2 (water) should heal 5 hp per sec but it's capped at max_hp, so it stays at 100
    assert b2.hp == 100.0

    # Check obstacles
    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].radius == 30.0
