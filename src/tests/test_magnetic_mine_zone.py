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

    # Place a ball at (200, 200)
    b = MockBall(200, 200, 0, 0)
    mode.setup(world, [b])

    # Place a mine at (300, 200) -> distance is 100, which is within the 150 tracking distance
    mode.mines = [{
        "x": 300.0,
        "y": 200.0,
        "radius": 15.0,
        "damage": 50.0,
        "active": True
    }]

    orig_x = b.x
    mode.tick(world, [b], delta=1.0)

    # Ball should be dragged towards the mine (x increases)
    assert b.x > orig_x
    # Mine should not move
    assert mode.mines[0]["x"] == 300.0

def test_magnetic_mine_explosion():
    mode = MagneticMineZoneMode()
    world = MockWorld()

    # Ball 1 touches the mine
    b1 = MockBall(200, 200, 0, 0)
    # Ball 2 is within explosion radius (200) but not touching
    b2 = MockBall(250, 200, 0, 0)
    # Ball 3 is outside explosion radius
    b3 = MockBall(500, 500, 0, 0)

    mode.setup(world, [b1, b2, b3])

    # Mine at same pos as b1
    mode.mines = [{
        "x": 200.0,
        "y": 200.0,
        "radius": 15.0,
        "damage": 50.0,
        "active": True
    }]

    mode.tick(world, [b1, b2, b3], delta=1.0)

    assert not mode.mines[0]["active"]
    assert b1.hp == 50
    assert b2.hp == 50  # b2 should also take damage due to massive shockwave
    assert b3.hp == 100 # b3 should not take damage
    assert len(world.events) == 1
    assert world.events[0][0] == "mine_explosion"
