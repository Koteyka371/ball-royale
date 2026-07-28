import pytest
import math
from src.ai.game_modes import GAME_MODES, NetworkedBlackHolesMode

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards

class MockWorld:
    def __init__(self, hazards):
        self.arena = MockArena(hazards)
        self.events = []

    def add_event(self, event_type, data):
        self.events.append({"type": event_type, "data": data})

class MockHazard:
    def __init__(self, h_id, x, y, kind):
        self.id = h_id
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 50.0

class MockBall:
    def __init__(self, b_id, x, y):
        self.id = b_id
        self.x = x
        self.y = y
        self.vx = 10.0
        self.vy = 10.0
        self.alive = True
        self.teleport_cooldown = 0.0

def test_networked_black_holes_exists():
    assert "networked_black_holes" in GAME_MODES
    assert isinstance(GAME_MODES["networked_black_holes"], NetworkedBlackHolesMode)

def test_network_activation():
    mode = GAME_MODES["networked_black_holes"]
    mode.network_active = False
    mode.timer = 0.0

    world = MockWorld([])
    balls = []

    # Needs to reach cooldown (10.0)
    mode.tick(world, balls, delta=10.0)

    assert mode.network_active == True
    assert len(world.events) == 1
    assert world.events[0]["type"] == "network_activated"

def test_network_deactivation():
    mode = GAME_MODES["networked_black_holes"]
    mode.network_active = True
    mode.timer = 0.0

    world = MockWorld([])
    balls = []

    # Needs to reach duration (5.0)
    mode.tick(world, balls, delta=5.0)

    assert mode.network_active == False
    assert len(world.events) == 1
    assert world.events[0]["type"] == "network_deactivated"

def test_teleportation():
    mode = GAME_MODES["networked_black_holes"]
    mode.network_active = True
    mode.timer = 0.0

    bh1 = MockHazard(1, 100, 100, "black_hole")
    bh2 = MockHazard(2, 500, 500, "massive_black_hole")

    world = MockWorld([bh1, bh2])

    # Ball inside bh1 radius
    ball = MockBall(1, 110, 110)
    balls = [ball]

    mode.tick(world, balls, delta=0.016)

    # Should teleport to bh2 (x=500, y=500)
    assert ball.x == 500
    assert ball.y == 500
    assert ball.vx == 0.0
    assert ball.vy == 0.0
    assert ball.teleport_cooldown == 2.0

    # Event should be added
    teleport_events = [e for e in world.events if e["type"] == "black_hole_teleport"]
    assert len(teleport_events) == 1

def test_teleport_cooldown():
    mode = GAME_MODES["networked_black_holes"]
    mode.network_active = True
    mode.timer = 0.0

    bh1 = MockHazard(1, 100, 100, "black_hole")
    bh2 = MockHazard(2, 500, 500, "massive_black_hole")

    world = MockWorld([bh1, bh2])

    # Ball inside bh1 radius but with cooldown
    ball = MockBall(1, 110, 110)
    ball.teleport_cooldown = 1.0
    balls = [ball]

    mode.tick(world, balls, delta=0.016)

    # Should not teleport
    assert ball.x == 110
    assert ball.y == 110

    # Cooldown should be reduced
    assert math.isclose(ball.teleport_cooldown, 1.0 - 0.016, abs_tol=1e-5)
