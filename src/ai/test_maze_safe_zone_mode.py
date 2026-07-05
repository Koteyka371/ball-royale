import pytest
from ai.game_modes import MazeSafeZoneMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []

class MockBall:
    def __init__(self, ball_id):
        self.id = ball_id
        self.x = 500.0
        self.y = 500.0
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 20.0
        self.hp = 100.0
        self.alive = True
        self.ball_type = "player"
        self.team = "player"

def test_maze_safe_zone_mode_setup():
    mode = MazeSafeZoneMode()
    world = MockWorld()
    balls = [MockBall(1), MockBall(2)]

    mode.setup(world, balls)

    # Check if maze walls generated
    assert len(mode.walls) > 0
    # Check if safe zone setup
    assert mode.zone_radius == 500.0
    assert mode.zone_x == 500.0
    assert mode.zone_y == 500.0

def test_maze_safe_zone_mode_tick_damage():
    mode = MazeSafeZoneMode()
    world = MockWorld()
    ball = MockBall(1)

    mode.setup(world, [ball])

    # Move ball way outside the safe zone
    ball.x = -1000.0
    ball.y = -1000.0

    initial_hp = ball.hp
    mode.tick(world, [ball], 1.0)

    # Should take damage from being outside safe zone
    assert ball.hp < initial_hp

def test_maze_safe_zone_mode_tick_maze_collision():
    mode = MazeSafeZoneMode()
    world = MockWorld()
    ball = MockBall(1)

    mode.setup(world, [ball])

    # Find a wall and place the ball inside it
    assert len(mode.walls) > 0
    wall = mode.walls[0]
    ball.x = wall["x"] + wall["width"] / 2.0
    ball.y = wall["y"] + wall["height"] / 2.0

    # Make sure ball is inside the safe zone so it only takes wall damage
    mode.zone_x = ball.x
    mode.zone_y = ball.y
    mode.zone_radius = 500.0

    initial_hp = ball.hp
    mode.tick(world, [ball], 1.0)

    # Should take damage from touching the wall
    assert ball.hp < initial_hp
