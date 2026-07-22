from ai.game_modes import ThermalFreezeTagMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []
        self.events = []

    def add_event(self, name, data):
        self.events.append((name, data))

class MockBall:
    def __init__(self, x=0, y=0, radius=10, is_frozen=False, hp=100.0):
        self.id = id(self)
        self.x = x
        self.y = y
        self.radius = radius
        self.is_frozen = is_frozen
        self.hp = hp
        self.alive = True
        self.ball_type = "normal"
        self._frost_last_hp = hp
        self.stun_timer = 0.0
        self.frozen_timer = 0.0
        self.thaw_progress = 0.0
        self.is_bouncy = False
        self.is_ghost = False
        self.gravity_scale = 1.0
        self.friction_multiplier = 1.0

def test_thermal_thawing():
    world = MockWorld()
    mode = ThermalFreezeTagMode()
    b = MockBall(x=500, y=500, is_frozen=True)
    balls = [b]

    class MockHazard:
        def __init__(self, x, y, radius, kind):
            self.x = x
            self.y = y
            self.radius = radius
            self.kind = kind
            self.duration = 10.0

    h = MockHazard(500, 500, 150, "heat_zone")
    world.arena.hazards.append(h)

    mode.tick(world, balls, delta=1.5)
    assert b.is_frozen
    assert b.thaw_progress == 1.5

    mode.tick(world, balls, delta=1.5)
    assert not b.is_frozen

def test_frost_shattering():
    world = MockWorld()
    mode = ThermalFreezeTagMode()
    b = MockBall(x=500, y=500, is_frozen=True)
    b._frost_last_hp = 100.0
    balls = [b]

    class MockHazard:
        def __init__(self, x, y, radius, kind):
            self.x = x
            self.y = y
            self.radius = radius
            self.kind = kind
            self.duration = 10.0

    h = MockHazard(500, 500, 150, "frost_zone")
    world.arena.hazards.append(h)

    b.hp = 90.0 # took damage
    mode.tick(world, balls, delta=0.1)

    assert not b.alive
    assert b.hp == 0.0
    assert b.id in world.dead_balls

    event_found = False
    for event_name, event_data in world.events:
        if event_name == 'ball_died' and event_data.get('reason') == 'shattered' and event_data.get('id') == b.id:
            event_found = True
            break
    assert event_found
