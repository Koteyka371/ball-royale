import pytest
from ai.random_teleporter import RandomTeleporterMode

class DummyArena:
    def __init__(self):
        self.width = 800
        self.height = 600

class DummyWorld:
    def __init__(self):
        self.arena = DummyArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class DummyBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.radius = 10.0
        self.vx = 50.0
        self.vy = 50.0

def test_random_teleporter_unlinked():
    import random
    mode = RandomTeleporterMode()
    world = DummyWorld()
    balls = [DummyBall(100, 100)]
    balls[0].vx = 50.0
    balls[0].vy = 50.0

    # Force unlinked portal spawn
    random.seed(1)

    # Tick past spawn interval
    while len(mode.portals) == 0:
        mode.tick(world, balls, delta=0.1)

    # Need an unlinked portal for this test
    if "link" in mode.portals[0]:
        mode.portals = []
        random.seed(42)
        while len(mode.portals) == 0:
            mode.tick(world, balls, delta=0.1)

    assert len(mode.portals) > 0
    portal = mode.portals[0]

    # Move ball into portal
    balls[0].x = portal["x"]
    balls[0].y = portal["y"]

    mode.tick(world, balls, delta=0.1)

    # Ball should have teleported
    assert balls[0].x != portal["x"] or balls[0].y != portal["y"]

    # Velocity should be reset to 0 for unlinked
    assert balls[0].vx == 0.0
    assert balls[0].vy == 0.0

    event_types = [e[0] for e in world.events]
    assert "portal_spawn" in event_types
    assert "teleport_out" in event_types
    assert "teleport_in" in event_types

def test_random_teleporter_linked():
    import random
    mode = RandomTeleporterMode()
    world = DummyWorld()
    balls = [DummyBall(100, 100)]
    balls[0].vx = 50.0
    balls[0].vy = 50.0

    # Tick past spawn interval and force linked portal spawn
    mode.spawn_timer = 5.0

    # Temporarily monkeypatch random to guarantee linked portals
    orig_random = random.random
    random.random = lambda: 0.1
    try:
        mode.tick(world, balls, delta=0.1)
    finally:
        random.random = orig_random

    assert len(mode.portals) == 2
    portal = mode.portals[0]
    linked = portal["link"]

    # Move ball into portal
    balls[0].x = portal["x"]
    balls[0].y = portal["y"]

    mode.tick(world, balls, delta=0.1)

    # Ball should have teleported to linked portal
    assert balls[0].x == linked["x"]
    assert balls[0].y == linked["y"]

    # Velocity should NOT be reset for linked
    assert balls[0].vx == 50.0
    assert balls[0].vy == 50.0

    event_types = [e[0] for e in world.events]
    assert "portal_spawn" in event_types
    assert "teleport_out" in event_types
    assert "teleport_in" in event_types
