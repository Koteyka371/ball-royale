import pytest
from ai.black_hole_anomaly import BlackHoleAnomalyMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.projectiles = []
        self.boosters = []
        self.events = []

    def add_event(self, kind, data):
        self.events.append({"kind": kind, "data": data})

class MockProjectile:
    def __init__(self, x, y, vx, vy, ball_type="projectile"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.ball_type = ball_type

class MockItem:
    def __init__(self, x, y, vx=0, vy=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

def test_black_hole_anomaly_activation():
    mode = BlackHoleAnomalyMode()
    world = MockWorld()

    mode.setup(world, [])
    assert not mode.active

    # Tick until active
    mode.tick(world, [], delta=10.0)
    assert mode.active
    assert mode.active_timer == 5.0
    assert any(e["kind"] == "anomaly_spawn" for e in world.events)

    # Tick until inactive
    mode.tick(world, [], delta=5.0)
    assert not mode.active
    assert mode.anomaly_timer == 10.0
    assert any(e["kind"] == "anomaly_despawn" for e in world.events)

def test_black_hole_anomaly_pulls_projectiles():
    mode = BlackHoleAnomalyMode()
    world = MockWorld()

    mode.setup(world, [])

    # Force active and set position
    mode.active = True
    mode.active_timer = 5.0
    mode.x = 500.0
    mode.y = 500.0
    mode.radius = 300.0
    mode.pull_strength = 200.0

    proj1 = MockProjectile(250.0, 500.0, 0.0, 0.0)
    proj2 = MockProjectile(800.0, 800.0, 0.0, 0.0) # Out of radius (dist ~424 > 300)
    world.projectiles = [proj1, proj2]

    mode.tick(world, [], delta=1.0)

    # Proj1 should be pulled towards center (500, 500)
    assert proj1.vx > 0.0
    assert proj1.vy == 0.0

    # Proj2 should be unaffected
    assert proj2.vx == 0.0
    assert proj2.vy == 0.0

def test_black_hole_anomaly_pulls_items():
    mode = BlackHoleAnomalyMode()
    world = MockWorld()

    mode.setup(world, [])
    mode.active = True
    mode.active_timer = 5.0
    mode.x = 500.0
    mode.y = 500.0

    hazard = MockItem(500.0, 250.0)
    booster = {"x": 500.0, "y": 700.0} # Testing dictionary item

    world.arena.hazards = [hazard]
    world.boosters = [booster]

    mode.tick(world, [], delta=1.0)

    # Hazard should move towards center (500, 500)
    assert hazard.x == 500.0
    assert hazard.vy > 0.0

    # Booster (dictionary) should move towards center
    assert booster["x"] == 500.0
    assert booster["y"] < 700.0
