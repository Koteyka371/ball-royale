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

def test_massive_gravity_well_pulls_projectiles_and_items():
    from ai.game_modes import GAME_MODES
    import ai.game_modes
    mode = GAME_MODES.get('massive_gravity_well_event') or GAME_MODES.get('massive_gravity_well')
    if not mode:
        for name, m in ai.game_modes.GAME_MODES.items():
            if "MassiveGravityWellMode" in str(type(m)):
                mode = m
                break

    assert mode is not None

    class MockWorld:
        def __init__(self):
            self.projectiles = []
            self.items = []
            self.arena = type('MockArena', (), {'width': 1000, 'height': 1000, 'hazards': []})()
        def add_event(self, *args, **kwargs): pass

    class MockEntity:
        def __init__(self, x, y, vx=0, vy=0):
            self.x = x
            self.y = y
            self.vx = vx
            self.vy = vy

    world = MockWorld()
    proj_pull = MockEntity(500, 400, vx=0, vy=0)
    proj_consume = MockEntity(500, 510, vx=0, vy=0)
    world.projectiles = [proj_pull, proj_consume]

    item_pull = MockEntity(500, 600, vx=0, vy=0)
    item_consume = MockEntity(500, 490, vx=0, vy=0)
    world.items = [item_pull, item_consume]

    mode.mgw_x = 500
    mode.mgw_y = 500
    mode.mgw_radius = 50.0
    mode.spawned = True

    mode.tick(world, [], delta=0.1)

    assert len(world.projectiles) == 1
    assert proj_pull in world.projectiles
    assert proj_consume not in world.projectiles
    assert abs(proj_pull.vx) < 1.0
    assert proj_pull.vy > 0

    assert len(world.items) == 1
    assert item_pull in world.items
    assert item_consume not in world.items
    assert item_pull.y < 600
