import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.action import Action
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.boundary_states = {}
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.width = 1000
        self.height = 1000
        self.game_mode = None

class MockBall:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = 10.0
        self.hp = 100
        self.alive = True
        self.bumper_combo = 0

def test_trampoline_boundary_mode_setup():
    mode = GAME_MODES["trampoline_boundary"]
    world = MockWorld()
    mode.setup(world, [])
    assert world.arena.boundary_states["top"] == "trampoline"
    assert world.arena.boundary_states["bottom"] == "trampoline"
    assert world.arena.boundary_states["left"] == "trampoline"
    assert world.arena.boundary_states["right"] == "trampoline"

def test_trampoline_boundary_bounce():
    world = MockWorld()
    world.arena.boundary_states["top"] = "trampoline"

    # Ball hitting the top boundary
    ball = MockBall(500.0, 5.0, 0.0, -100.0)
    action = Action(ball, world)

    # Normally handle_wall_collisions is not exposed directly like this but we can test execute on a dummy strategy
    # Let's mock a method to test the logic
    # In Action.execute, if ball is out of bounds, it handles bouncing
    action.execute('idle', 0.1)

    # HP shouldn't decrease
    assert ball.hp == 100
    assert ball.alive

    # After bouncing off top, the ball should be sent downwards (vy > 0)
    # The new speed should be extreme
    import math
    speed = math.sqrt(ball.vx**2 + ball.vy**2)
    assert speed > 3000.0
    assert ball.vy > 0
