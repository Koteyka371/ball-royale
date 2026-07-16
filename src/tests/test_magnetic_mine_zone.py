import pytest
from ai.game_modes import MagneticMineZoneMode

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, name, data):
        self.events.append((name, data))

class MockBall:
    def __init__(self, x, y, vx, vy, radius=10.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.alive = True
        self.hp = 100

def test_magnetic_mine_pull():
    mode = MagneticMineZoneMode()
    world = MockWorld()

    # Fast ball (speed 150 -> norm 1 -> tracking 150)
    b_fast = MockBall(200, 200, 150, 0)
    mode.setup(world, [b_fast])

    # Place a mine at 300, 200. Distance = 100.
    # It should track because tracking = 150.
    mode.mines = [{
        "x": 300.0,
        "y": 200.0,
        "radius": 15.0,
        "damage": 50.0,
        "active": True
    }]

    orig_x = mode.mines[0]["x"]
    mode.tick(world, [b_fast], delta=1.0)
    assert mode.mines[0]["x"] < orig_x

    # Slow ball (speed 0 -> norm 0 -> tracking 50)
    b_slow = MockBall(200, 200, 0, 0)
    mode.mines = [{
        "x": 300.0,
        "y": 200.0,
        "radius": 15.0,
        "damage": 50.0,
        "active": True
    }]
    orig_x_slow = mode.mines[0]["x"]
    mode.tick(world, [b_slow], delta=1.0)
    # distance = 100. tracking = 50. Should NOT track!
    assert mode.mines[0]["x"] == orig_x_slow

def test_magnetic_mine_explosion():
    mode = MagneticMineZoneMode()
    world = MockWorld()
    b = MockBall(200, 200, 0, 0)
    mode.setup(world, [b])
    mode.mines = [{
        "x": 200.0,
        "y": 200.0,
        "radius": 15.0,
        "damage": 50.0,
        "active": True
    }]

    mode.tick(world, [b], delta=1.0)
    assert not mode.mines[0]["active"]
    assert b.hp == 50
    assert len(world.events) == 1
    assert world.events[0][0] == "mine_explosion"

