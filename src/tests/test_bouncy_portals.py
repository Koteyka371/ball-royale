import pytest
import math
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id, x, y, radius, alive=True):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = radius
        self.alive = alive

class MockHazard:
    def __init__(self, id, x, y, radius, active=True):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = radius
        self.active = active

class MockArena:
    def __init__(self):
        self.width = 800
        self.height = 600
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
    def add_event(self, name, data):
        self.events.append((name, data))

def test_bouncy_portals_mode():
    assert "bouncy_portals" in GAME_MODES
    mode = GAME_MODES["bouncy_portals"]
    mode.portals = []
    mode.spawn_timer = 0.0

    world = MockWorld()
    balls = [MockBall("b1", 400, 300, 10)]

    # Fast forward to spawn portals
    for _ in range(500):
        mode.tick(world, balls, 0.016)
        if mode.portals:
            break

    assert len(mode.portals) > 0
    portal = mode.portals[0]

    # Test ball reflection
    portal["x"] = 400
    portal["y"] = 400
    portal["nx"] = 0
    portal["ny"] = -1 # Facing UP

    ball = balls[0]
    ball.x = 400
    ball.y = 390
    ball.vx = 0
    ball.vy = 50 # Moving DOWN (into portal face)

    mode.tick(world, balls, 0.016)

    # Should bounce back up with multiplier
    assert ball.vy < 0
    assert abs(ball.vy) == 50 * 1.5

    # Test hazard reflection
    hazard = MockHazard("h1", 400, 390, 10)
    hazard.vx = 0
    hazard.vy = 100
    world.arena.hazards.append(hazard)

    mode.tick(world, balls, 0.016)

    assert hazard.vy < 0
    assert abs(hazard.vy) == 100
