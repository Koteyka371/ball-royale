import pytest
import math
from ai.game_modes import MovingWallsMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
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

def test_moving_walls_spawn():
    mode = MovingWallsMode()
    world = MockWorld()
    balls = [MockBall(500, 500)]

    # Tick past spawn timer
    mode.spawn_timer = 0.0
    mode.tick(world, balls, delta=5.1)

    # Should spawn a wall
    assert len(world.arena.hazards) > 0
    wall = world.arena.hazards[0]
    assert wall["kind"] == "moving_wall"
    assert "vx" in wall
    assert "vy" in wall

    # Check if wall moves
    initial_x = wall["x"]
    initial_y = wall["y"]
    mode.tick(world, balls, delta=1.0)
    assert wall["x"] != initial_x or wall["y"] != initial_y

def test_moving_walls_collision():
    mode = MovingWallsMode()
    world = MockWorld()
    ball = MockBall(500, 500)
    balls = [ball]

    wall = {
        "kind": "moving_wall",
        "x": 500,
        "y": 500,
        "width": 100,
        "height": 100,
        "vx": 50.0,
        "vy": 0.0,
        "damage": 20.0,
        "duration": 15.0,
        "id": "wall_1"
    }
    world.arena.hazards.append(wall)

    mode.tick(world, balls, delta=1.0)

    # Ball should be damaged
    assert ball.hp < 100.0
    # Ball should be pushed
    assert ball.x > 500 or ball.y != 500
    assert ball.vx != 0.0 or ball.vy != 0.0

def test_moving_walls_despawn():
    mode = MovingWallsMode()
    world = MockWorld()
    balls = []

    wall = {
        "kind": "moving_wall",
        "x": 500,
        "y": 500,
        "width": 100,
        "height": 100,
        "vx": 50.0,
        "vy": 0.0,
        "damage": 20.0,
        "duration": 0.5,
        "id": "wall_1"
    }
    world.arena.hazards.append(wall)

    mode.spawn_timer = 100.0
    mode.tick(world, balls, delta=1.0)

    # Wall should be despawned
    assert len(world.arena.hazards) == 0
