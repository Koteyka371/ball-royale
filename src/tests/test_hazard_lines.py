import pytest
import math
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.tick_count = 0

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 20.0
        self.hp = 100.0
        self.alive = True
        self.is_intangible = False

def test_hazard_lines_spawn():
    mode = GAME_MODES["hazard_lines"]
    world = MockWorld()
    balls = [MockBall(500, 500)]

    # Tick past spawn timer
    mode.spawn_timer = 0.0
    mode.tick(world, balls, delta=3.1)

    # Should spawn a hazard line
    assert len(world.arena.hazards) > 0
    hazard = world.arena.hazards[0]
    assert hazard["kind"] == "hazard_line"
    assert "vx" in hazard
    assert "vy" in hazard
    assert hazard["width"] == 1000.0 or hazard["height"] == 1000.0

    # Check if hazard moves
    initial_x = hazard["x"]
    initial_y = hazard["y"]
    mode.tick(world, balls, delta=1.0)
    assert hazard["x"] != initial_x or hazard["y"] != initial_y

def test_hazard_lines_collision():
    mode = GAME_MODES["hazard_lines"]
    world = MockWorld()
    ball = MockBall(500, 500)
    balls = [ball]

    line = {
        "kind": "hazard_line",
        "x": 500,
        "y": 500,
        "width": 1000.0,
        "height": 10.0,
        "vx": 0.0,
        "vy": 0.0,
        "damage": 30.0,
        "duration": 15.0,
        "id": "line_1"
    }
    world.arena.hazards.append(line)

    mode.tick(world, balls, delta=1.0)

    # Ball should be damaged
    assert ball.hp < 100.0

def test_hazard_lines_despawn():
    mode = GAME_MODES["hazard_lines"]
    world = MockWorld()
    balls = []

    line = {
        "kind": "hazard_line",
        "x": 500,
        "y": 500,
        "width": 1000.0,
        "height": 10.0,
        "vx": 0.0,
        "vy": 0.0,
        "damage": 30.0,
        "duration": 0.5,
        "id": "line_1"
    }
    world.arena.hazards.append(line)

    mode.spawn_timer = 100.0
    mode.tick(world, balls, delta=1.0)

    # Hazard should be despawned
    assert len(world.arena.hazards) == 0
