import pytest
from unittest.mock import MagicMock
from ai.game_modes import QuantumTetherZoneMode

class MockArena:
    def __init__(self):
        self.width = 800
        self.height = 600
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, id, x, y, hp=100.0, ball_type="player"):
        self.id = id
        self.x = x
        self.y = y
        self.hp = hp
        self.ball_type = ball_type

def test_quantum_tether_zone_setup():
    mode = QuantumTetherZoneMode()
    world = MockWorld()
    balls = [MockBall(1, 100, 100), MockBall(2, 200, 200)]

    mode.setup(world, balls)

    assert len(mode.zones) == 1
    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].kind == "quantum_tether_zone"

def test_tether_formation():
    mode = QuantumTetherZoneMode()
    world = MockWorld()

    b1 = MockBall(1, 100, 100)
    b2 = MockBall(2, 110, 110)
    b3 = MockBall(3, 700, 700) # Outside zone

    balls = [b1, b2, b3]

    mode.setup(world, balls)

    # Force zone position
    mode.zones[0]["x"] = 100
    mode.zones[0]["y"] = 100

    mode.tick(world, balls, 0.1)

    assert b1.id in mode.tethers
    assert b2.id in mode.tethers
    assert b3.id not in mode.tethers

    assert mode.tethers[b1.id] == b2
    assert mode.tethers[b2.id] == b1

    assert getattr(b1, "quantum_tether_target", None) == b2
    assert getattr(b2, "quantum_tether_target", None) == b1

def test_damage_sharing():
    mode = QuantumTetherZoneMode()
    world = MockWorld()

    b1 = MockBall(1, 100, 100)
    b2 = MockBall(2, 110, 110)
    balls = [b1, b2]

    mode.setup(world, balls)
    mode.zones[0]["x"] = 100
    mode.zones[0]["y"] = 100

    mode.tick(world, balls, 0.1)

    # b1 takes damage
    b1.hp -= 20

    mode.tick(world, balls, 0.1)

    assert b2.hp == 80 # damage should be shared

    # b2 takes damage
    b2.hp -= 10

    mode.tick(world, balls, 0.1)
    assert b1.hp == 70

def test_tether_snap():
    mode = QuantumTetherZoneMode()
    world = MockWorld()

    b1 = MockBall(1, 100, 100)
    b2 = MockBall(2, 110, 110)
    balls = [b1, b2]

    mode.setup(world, balls)
    mode.zones[0]["x"] = 100
    mode.zones[0]["y"] = 100

    mode.tick(world, balls, 0.1)

    # Move them far apart
    b1.x = 0
    b2.x = 500 # distance 500, > snap_distance (400)

    mode.tick(world, balls, 0.1)

    assert b1.hp == 50 # 100 - 50 snap damage
    assert b2.hp == 50
    assert b1.id not in mode.tethers
    assert b2.id not in mode.tethers

    # Check event
    assert any(e[0] == "quantum_tether_snap" for e in world.events)

def test_dead_ball_tether_breaks():
    mode = QuantumTetherZoneMode()
    world = MockWorld()

    b1 = MockBall(1, 100, 100)
    b2 = MockBall(2, 110, 110)
    balls = [b1, b2]

    mode.setup(world, balls)
    mode.zones[0]["x"] = 100
    mode.zones[0]["y"] = 100

    mode.tick(world, balls, 0.1)

    # Target dies
    b2.hp = 0

    mode.tick(world, balls, 0.1)

    assert b1.id not in mode.tethers
    assert getattr(b1, "quantum_tether_target", None) is None
