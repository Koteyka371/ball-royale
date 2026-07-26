import pytest
from ai.game_modes import BlackHoleAnomalyMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.projectiles = []
        self.boosters = []
        self.events = []

    def add_event(self, name, data):
        self.events.append((name, data))

class MockBall:
    def __init__(self, x, y, alive=True):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.alive = alive

class MockProjectile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0

class MockBooster:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def test_black_hole_anomaly_activation():
    mode = BlackHoleAnomalyMode()
    world = MockWorld()

    # Not active initially, timer goes down
    mode.tick(world, [], delta=15.0)
    assert mode.active == True
    assert mode.x == 500.0
    assert mode.y == 500.0

    # Active, timer goes down, then inactive
    mode.tick(world, [], delta=10.0)
    assert mode.active == False

def test_black_hole_anomaly_pull():
    mode = BlackHoleAnomalyMode()
    world = MockWorld()

    # Activate anomaly
    mode.tick(world, [], delta=15.0)

    b = MockBall(200.0, 500.0) # Left of center (500, 500)
    p = MockProjectile(200.0, 500.0)
    item = MockBooster(200.0, 500.0)

    world.projectiles.append(p)
    world.boosters.append(item)

    mode.tick(world, [b], delta=1.0)

    # They should be pulled right (positive x velocity/movement)
    assert b.vx > 0
    assert p.vx > 0
    assert item.x > 200.0
