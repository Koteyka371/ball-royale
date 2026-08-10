import pytest
from ai.random_portals import RandomPortalsMode

class MockArena:
    def __init__(self):
        self.width = 800
        self.height = 600

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.vx = 50
        self.vy = 50
        self.radius = 10
        self.alive = True
        self.id = 1

def test_random_portals_spawn():
    mode = RandomPortalsMode()
    world = MockWorld()
    balls = [MockBall(0, 0)]

    mode.setup(world, balls)

    assert len(mode.portals) == 4
    for p in mode.portals:
        assert 100 <= p["x"] <= 700
        assert 100 <= p["y"] <= 500

def test_random_portals_teleport():
    import math
    mode = RandomPortalsMode()
    world = MockWorld()
    b = MockBall(0, 0)
    balls = [b]

    mode.setup(world, balls)

    p1 = mode.portals[0]
    # Move ball into portal 1
    b.x = p1["x"]
    b.y = p1["y"]

    mode.tick(world, balls, delta=0.016)

    v_len = math.hypot(b.vx, b.vy)
    nx = b.vx / v_len
    ny = b.vy / v_len
    offset = p1["radius"] + b.radius + 5.0

    # Check that ball was teleported to one of the other portals
    # at the correct offset based on velocity
    teleported_to_other = False
    for p in mode.portals[1:]:
        target_x = p["x"] + nx * offset
        target_y = p["y"] + ny * offset
        if math.isclose(b.x, target_x, abs_tol=0.1) and math.isclose(b.y, target_y, abs_tol=0.1):
            teleported_to_other = True
            break

    assert teleported_to_other, "Ball should have teleported to another portal at the correct offset"

    # Ball shouldn't instantly teleport if placed just outside the offset
    # since it's > p["radius"] + b.radius
    b.x = p1["x"] + nx * (offset + 1.0)
    b.y = p1["y"] + ny * (offset + 1.0)

    start_x = b.x
    start_y = b.y

    mode.tick(world, balls, delta=0.016)

    # Shouldn't teleport
    assert b.x == start_x
    assert b.y == start_y

def test_random_portals_respawn_interval():
    mode = RandomPortalsMode()
    world = MockWorld()
    balls = [MockBall(0, 0)]

    mode.setup(world, balls)

    original_portals = mode.portals.copy()

    mode.tick(world, balls, delta=19.0)

    # Portals should be the same
    assert mode.portals == original_portals

    mode.tick(world, balls, delta=2.0)

    # Teleport interval passed, portals should have respawned
    # While they could theoretically be same, probability is essentially 0
    assert mode.portals != original_portals
