import sys; sys.path.append('src')
import pytest
import math
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []
        self.next_id = 100

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, bid, x, y):
        self.id = bid
        self.alive = True
        self.ball_type = "player"
        self.x = x
        self.y = y
        self.vx = 10.0
        self.vy = 0.0
        self.is_dashing = False
        self.damage = 20.0
        self.hp = 100.0

def test_quantum_clone_field_records_history():
    mode = GAME_MODES["quantum_clone_field"]
    world = MockWorld()
    b = MockBall("b1", 100.0, 100.0)
    world.balls = [b]

    mode.setup(world, world.balls)

    # Tick to record history
    b.x = 110.0
    mode.tick(world, world.balls, 0.1)

    assert hasattr(b, "_quantum_history")
    assert len(b._quantum_history) == 1
    assert b._quantum_history[0]["x"] == 110.0

def test_quantum_clone_field_spawns_clone_on_dash():
    mode = GAME_MODES["quantum_clone_field"]
    world = MockWorld()
    b = MockBall("b1", 500.0, 500.0)
    world.balls = [b]

    mode.setup(world, world.balls)

    # Force a field at the ball's location
    mode.fields = [{
        "x": 500.0,
        "y": 500.0,
        "radius": 150.0,
        "life": 10.0
    }]

    # Record some history
    mode.tick(world, world.balls, 0.1)

    # Dash through the field
    b.is_dashing = True
    mode.tick(world, world.balls, 0.1)

    # Clone should be spawned
    clones = [c for c in world.balls if getattr(c, "is_quantum_clone", False)]
    assert len(clones) == 1

    clone = clones[0]
    assert clone.hp == 1.0
    assert clone.damage == b.damage * 0.5
    assert hasattr(clone, "playback_history")

    # Clone should play back history on next tick
    b.is_dashing = False

    mode.tick(world, world.balls, 0.1)
    # The clone should have its x/y updated based on history
    assert clone.x == 500.0
