import pytest
import sys
import os

# Append src to sys.path so backend modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.game_modes import EscortMode

class MockBall:
    def __init__(self, team, x, y, id=0):
        self.team = team
        self.x = x
        self.y = y
        self.alive = True
        self.ball_type = "player"
        self.speed_boost_timer = 0.0
        self.id = id

class MockHazard:
    def __init__(self, kind, x, y, team=None):
        self.kind = kind
        self.x = x
        self.y = y
        self.team = team
        self.radius = 40.0

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

def test_payload_speed_pad_deployment_when_teammate_near():
    mode = EscortMode()
    world = MockWorld()

    payload = MockBall("Defenders", 100, 500, id=0)
    payload.is_payload = True
    payload.hp = 5000.0
    payload.speed = 1.0
    mode.payload = payload

    # Teammate close to payload
    b1 = MockBall("Defenders", 120, 500, id=1)

    balls = [payload, b1]

    # Tick for less than 10 seconds, no pad should deploy
    mode.tick(world, balls, 9.0)
    assert not any(h.kind == "bounce_pad" for h in world.arena.hazards)

    # Tick to cross 10.0 seconds threshold
    mode.tick(world, balls, 2.0)

    # Pad should deploy
    assert any(h.kind == "bounce_pad" for h in world.arena.hazards)

    pad = next(h for h in world.arena.hazards if h.kind == "bounce_pad")
    assert getattr(pad, "duration", 0) == 10.0
    assert getattr(pad, "team", "") == "Defenders"

def test_payload_speed_pad_no_deployment_when_alone_or_enemies_only():
    mode = EscortMode()
    world = MockWorld()

    payload = MockBall("Defenders", 100, 500, id=0)
    payload.is_payload = True
    payload.hp = 5000.0
    payload.speed = 1.0
    mode.payload = payload

    # Teammate far from payload
    b1 = MockBall("Defenders", 500, 500, id=1)
    # Enemy close to payload
    b2 = MockBall("Attackers", 120, 500, id=2)

    balls = [payload, b1, b2]

    # Tick beyond 10.0 seconds threshold
    mode.tick(world, balls, 11.0)

    # Pad should NOT deploy because no teammates are close
    assert not any(h.kind == "bounce_pad" for h in world.arena.hazards)
