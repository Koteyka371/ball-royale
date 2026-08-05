import pytest
from ai.game_modes import GameMode, GAME_MODES

class MockBall:
    def __init__(self, id, x, y, vx, vy, radius=15.0):
        self.id = id
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.alive = True
        self.ball_type = "normal"

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.projectiles = []

def test_shifting_mirror_walls_mode():
    world = MockWorld()

    ball1 = MockBall(1, 100.0, 100.0, 10.0, 5.0)

    balls = [ball1]

    mode = GAME_MODES["shifting_mirror_walls"]

    # Setup
    mode.setup(world, balls)

    # Assert walls created
    assert len(mode.walls) >= 2

    # Setup a specific wall for testing reflection
    mode.walls = [
        {"axis": "x", "pos": 200.0},
        {"axis": "y", "pos": 300.0}
    ]

    # Test x reflection
    ball2 = MockBall(2, 190.0, 100.0, 50.0, 0.0) # Moving right towards x=200
    balls.append(ball2)

    mode.shift_timer = 15.0
    mode.tick(world, balls, 0.016)

    assert ball2.vx == -50.0 # Reflected!
    assert ball2.x == 200.0 - ball2.radius

    # Test y reflection
    ball3 = MockBall(3, 100.0, 290.0, 0.0, 50.0) # Moving down towards y=300
    balls.append(ball3)

    mode.shift_timer = 15.0
    mode.tick(world, balls, 0.016)

    assert ball3.vy == -50.0 # Reflected!
    assert ball3.y == 300.0 - ball3.radius

    # Test timer shifts walls
    old_walls = list(mode.walls)
    mode.shift_timer = 0.0
    mode.tick(world, balls, 0.016)
    assert mode.walls != old_walls
    assert mode.shift_timer == 15.0

    # Test reflection for projectiles
    proj1 = MockBall(4, 190.0, 100.0, 1000.0, 0.0, radius=5.0)
    proj1.ball_type = "projectile"
    world.projectiles.append(proj1)

    mode.walls = [
        {"axis": "x", "pos": 200.0},
    ]

    mode.shift_timer = 15.0
    mode.tick(world, balls, 0.016)

    assert proj1.vx == -1000.0 # Reflected!
    assert proj1.x == 200.0 - proj1.radius
