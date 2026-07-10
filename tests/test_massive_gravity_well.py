class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.dead_balls = []

    def add_event(self, kind, data):
        self.events.append((kind, data))

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.hp = 100.0
        self.ball_type = "normal"
        self.team = "team1"

class MockHazard:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.vx = 0.0
        self.vy = 0.0

from ai.game_modes import MassiveGravityWellMode

def test_massive_gravity_well_basic():
    world = MockWorld()
    balls = [MockBall(500, 500)]

    mode = MassiveGravityWellMode()
    mode.setup(world, balls)

    assert mode.spawned == False

    mode.tick(world, balls, delta=0.1)

    assert mode.spawned == True
    assert mode.mgw_x > 0
    assert mode.mgw_y > 0
    assert mode.mgw_radius == 150.0

def test_massive_gravity_well_absorbs_hazards():
    world = MockWorld()
    balls = [MockBall(500, 500)]

    mode = MassiveGravityWellMode()
    mode.setup(world, balls)
    mode.tick(world, balls, delta=0.1)

    mode.mgw_x = 500.0
    mode.mgw_y = 500.0

    world.arena.hazards = [
        MockHazard(500, 500, "trap"),
        MockHazard(10, 10, "trap")
    ]

    mode.tick(world, balls, delta=0.1)

    assert len(world.arena.hazards) == 1
    assert mode.mgw_radius == 152.0

def test_massive_gravity_well_damages_players():
    world = MockWorld()
    balls = [MockBall(500, 500)]

    mode = MassiveGravityWellMode()
    mode.setup(world, balls)
    mode.tick(world, balls, delta=0.1)

    mode.mgw_x = 500.0
    mode.mgw_y = 500.0

    mode.tick(world, balls, delta=0.1)

    assert balls[0].hp < 100.0

def test_massive_gravity_well_pulls_players():
    world = MockWorld()
    balls = [MockBall(10, 10)]

    mode = MassiveGravityWellMode()
    mode.setup(world, balls)
    mode.tick(world, balls, delta=0.1)

    mode.mgw_x = 500.0
    mode.mgw_y = 500.0

    mode.tick(world, balls, delta=0.1)

    assert balls[0].x > 10.0
    assert balls[0].y > 10.0
