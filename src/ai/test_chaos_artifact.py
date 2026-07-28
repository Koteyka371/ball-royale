import pytest
from ai.game_modes import GAME_MODES
from ai.chaos_artifact import BALL_TYPES_LIST

class MockWorld:
    def __init__(self):
        self.events = []
        self.arena = type("MockArena", (), {"width": 800, "height": 600})()

    def add_event(self, name, data):
        self.events.append({"name": name, "data": data})

class MockBall:
    def __init__(self, id_val, x, y):
        self.id = id_val
        self.alive = True
        self.x = x
        self.y = y
        self.radius = 10.0
        self.base_speed = 100.0
        self.speed = 100.0
        self.base_damage = 10.0
        self.damage = 10.0
        self.ball_type = "basic"
        self.cosmetics = []

def test_chaos_artifact_spawn():
    world = MockWorld()
    mode = GAME_MODES["chaos_artifact"]
    mode.setup(world, [])

    balls = []

    mode.tick(world, balls, 0.1)

    assert mode.artifact is not None
    assert mode.holder_id is None
    assert any(e["name"] == "chaos_artifact_spawned" for e in world.events)

def test_chaos_artifact_pickup():
    world = MockWorld()
    mode = GAME_MODES["chaos_artifact"]
    mode.setup(world, [])

    # Force artifact to spawn at specific location
    mode.artifact = {"x": 100, "y": 100, "radius": 15.0}

    # Ball is overlapping
    b1 = MockBall("player1", 105, 105)
    balls = [b1]

    mode.tick(world, balls, 0.1)

    assert mode.holder_id == "player1"
    assert any(e["name"] == "chaos_artifact_picked_up" for e in world.events)

    # Check stats
    assert b1.speed == b1.base_speed * 2.0
    assert b1.damage == b1.base_damage * 3.0
    assert "chaos_aura" in b1.cosmetics

def test_chaos_artifact_randomize_type():
    world = MockWorld()
    mode = GAME_MODES["chaos_artifact"]
    mode.setup(world, [])

    b1 = MockBall("player1", 100, 100)
    balls = [b1]

    mode.artifact = {"x": 100, "y": 100, "radius": 15.0}
    mode.holder_id = "player1"
    mode.artifact_timer = 9.9

    orig_type = b1.ball_type

    mode.tick(world, balls, 0.2)

    # Timer should wrap around
    assert mode.artifact_timer < 0.2
    assert b1.ball_type in BALL_TYPES_LIST
    assert any(e["name"] == "chaos_artifact_randomized" for e in world.events)

def test_chaos_artifact_drop():
    world = MockWorld()
    mode = GAME_MODES["chaos_artifact"]
    mode.setup(world, [])

    b1 = MockBall("player1", 100, 100)
    balls = [b1]

    mode.artifact = {"x": 100, "y": 100, "radius": 15.0}
    mode.holder_id = "player1"

    # Kill the ball
    b1.alive = False

    mode.tick(world, balls, 0.1)

    assert mode.holder_id is None
    assert any(e["name"] == "chaos_artifact_dropped" for e in world.events)
