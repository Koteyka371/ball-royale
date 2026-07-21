import pytest
from ai.game_modes import GAME_MODES

class DummyArena:
    def __init__(self):
        self.width = 800
        self.height = 600
        self.hazards = [DummyHazard(200, 200)]

class DummyHazard:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10.0

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

def test_linked_portals_mode():
    mode = GAME_MODES['linked_portals']
    world = DummyWorld()
    balls = [DummyBall(100, 100)]

    # Tick past spawn interval
    for _ in range(600):
        mode.tick(world, balls, delta=0.01)

    assert len(mode.portals) >= 2
    portal = mode.portals[0]
    linked = portal["link"]

    # Save original velocity
    orig_vx = balls[0].vx
    orig_vy = balls[0].vy

    # Move ball into portal
    balls[0].x = portal["x"]
    balls[0].y = portal["y"]

    mode.tick(world, balls, delta=0.01)

    # Ball should have teleported to linked portal
    assert balls[0].x == linked["x"]
    assert balls[0].y == linked["y"]

    # Velocity should NOT be reset
    assert balls[0].vx == orig_vx
    assert balls[0].vy == orig_vy

    # Check hazard teleportation
    hazard = world.arena.hazards[0]
    portal["cooldown"] = 0.0
    hazard.x = portal["x"]
    hazard.y = portal["y"]

    mode.tick(world, balls, delta=0.01)
    assert hazard.x == linked["x"]
    assert hazard.y == linked["y"]
