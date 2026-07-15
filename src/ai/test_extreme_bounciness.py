import pytest
from ai.game_modes import GAME_MODES
from ai.action import Action
import math

class MockArena:
    def __init__(self):
        self.boundary_states = {}
        self.name = 'mock_arena'
        self.weather = 'clear'

    def clamp_position(self, x, y, r):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.arena = MockArena()
        self.game_mode = None
        self.events = []
        self.next_id = 9999

class MockBall:
    def __init__(self):
        self.id = 1
        self.ball_type = "basic"
        self.x = 0
        self.y = 500
        self.vx = -100
        self.vy = 0
        self.radius = 10.0
        self.hp = 100
        self.speed = 100

def test_extreme_bounciness():
    mode = GAME_MODES.get("extreme_bounciness")
    assert mode is not None
    assert mode.name == "Extreme Bounciness"

    world = MockWorld()
    world.game_mode = mode

    ball = MockBall()
    action = Action(ball, world)

    # Overwrite the _clamp_position method for testing reflection
    def override_clamp():
        # Force a bounce on the left wall
        if action.ball.x <= action.ball.radius:
            action.ball.x = action.ball.radius
            return True
        return False

    action._clamp_position = override_clamp

    action.execute("idle", 0.016)

    # original speed is 100. multiplied by 4 is 400.
    new_speed = math.sqrt(ball.vx**2 + ball.vy**2)
    assert new_speed > 350 # Roughly 400, accounting for angle randomness
    assert ball.hp == 100 # No damage from Extreme Bounciness / Mirror Walls
