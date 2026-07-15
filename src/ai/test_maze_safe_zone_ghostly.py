from ai.game_modes import MazeSafeZoneMode
import math

class MockBall:
    def __init__(self, t):
        self.ball_type = t
        self.alive = True
        self.team = ""
        self.x = 500.0
        self.y = 500.0
        self.hp = 100.0
        self.radius = 20.0

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []

def test_maze_safe_zone_ghostly():
    mode = MazeSafeZoneMode()
    world = MockWorld()
    ball = MockBall("player")
    balls = [ball]

    mode.setup(world, balls)

    mode.walls = [{
        "x": 490.0,
        "y": 490.0,
        "width": 20.0,
        "height": 20.0,
        "dx": 0.0,
        "dy": 0.0,
        "is_ghostly": True,
        "ghost_timer": 5.0
    }]

    mode.tick(world, balls, 0.1)
    assert ball.hp == 100.0
    assert ball.x == 500.0
    assert ball.y == 500.0

    mode.walls[0]["is_ghostly"] = False
    mode.tick(world, balls, 0.1)
    assert ball.hp < 100.0
    assert ball.x != 500.0 or ball.y != 500.0
