import pytest
from ai.game_modes import GAME_MODES, ConveyorBeltArenaMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, payload):
        self.events.append((event_type, payload))

class MockBall:
    def __init__(self, x=500.0, y=500.0):
        self.id = 1
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.ball_type = "default"

def test_conveyor_belt_mode_setup():
    mode = GAME_MODES["conveyor_belt_arena"]
    world = MockWorld()
    balls = [MockBall()]

    mode.setup(world, balls)

    # Check hazards were created
    assert len(world.arena.hazards) == 4
    kinds = [h.kind for h in world.arena.hazards]
    assert all(k == "spikes" for k in kinds)

def test_conveyor_belt_force_and_direction():
    mode = ConveyorBeltArenaMode()
    world = MockWorld()

    # Ball 1 in band 0 (y = 50 -> band 0 -> band_multiplier = 1.0)
    # Force = direction * band_multiplier = 1.0 * 1.0 = 1.0
    b1 = MockBall(x=500.0, y=50.0)

    # Ball 2 in band 1 (y = 150 -> band 1 -> band_multiplier = -1.0)
    # Force = direction * band_multiplier = 1.0 * -1.0 = -1.0
    b2 = MockBall(x=500.0, y=150.0)

    balls = [b1, b2]

    mode.setup(world, balls)

    # Tick with delta 1.0 for easy math
    # Force applied = direction * 150.0 * 1.0
    mode.tick(world, balls, delta=1.0)

    assert b1.vx > 0.0
    assert b1.vx == pytest.approx(150.0)

    assert b2.vx < 0.0
    assert b2.vx == pytest.approx(-150.0)

    # Fast forward 9 more seconds to trigger swap
    for _ in range(9):
        mode.tick(world, balls, delta=1.0)

    assert mode.conveyor_timer >= 0.0 # Timer should reset

    # Now the direction is reversed (conveyor_direction = -1.0)
    # Tick again to see the new forces applied

    # Reset velocities for clear observation
    b1.vx = 0.0
    b2.vx = 0.0

    mode.tick(world, balls, delta=1.0)

    # b1 band multiplier = 1.0, direction = -1.0 => negative force
    assert b1.vx < 0.0
    assert b1.vx == pytest.approx(-150.0)

    # b2 band multiplier = -1.0, direction = -1.0 => positive force
    assert b2.vx > 0.0
    assert b2.vx == pytest.approx(150.0)

    # Check event was emitted
    event_types = [e[0] for e in world.events]
    assert "conveyor_reverse" in event_types
