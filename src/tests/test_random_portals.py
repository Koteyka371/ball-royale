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
        assert "cooldown" not in p

def test_random_portals_teleport():
    import math
    mode = RandomPortalsMode()
    world = MockWorld()
    b = MockBall(0, 0)
    b.vx = 50
    b.vy = 0
    balls = [b]

    mode.setup(world, balls)

    p1 = mode.portals[0]
    # Move ball into portal 1
    b.x = p1["x"]
    b.y = p1["y"]

    mode.tick(world, balls, delta=0.016)

    # Check that ball was teleported to one of the other portals and offset
    teleported_to_other = False
    for p in mode.portals[1:]:
        dist = math.hypot(b.x - p["x"], b.y - p["y"])
        # Expected distance: portal_radius (40) + ball_radius (10) + 5.0 = 55.0
        if math.isclose(dist, 55.0, abs_tol=0.1):
            teleported_to_other = True
            break

    assert teleported_to_other, "Ball should have teleported to another portal and offset correctly"

    # Edge offset naturally prevents instant re-teleport
    old_x = b.x
    old_y = b.y
    mode.tick(world, balls, delta=0.016)
    assert b.x == old_x
    assert b.y == old_y

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
