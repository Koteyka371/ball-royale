import math
import pytest
from ai.game_modes import GAME_MODES
from ai.action import Action

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

def test_chaotic_pinball_machine_exists():
    mode = GAME_MODES.get("chaotic_pinball_machine")
    assert mode is not None
    assert mode.name == "Chaotic Pinball Machine"

def test_chaotic_pinball_machine_bounce():
    mode = GAME_MODES.get("chaotic_pinball_machine")
    world = MockWorld()
    world.game_mode = mode

    ball = MockBall()
    action = Action(ball, world)

    def override_clamp():
        # Force a bounce on the left wall
        if action.ball.x <= action.ball.radius:
            action.ball.x = action.ball.radius
            return True
        return False

    action._clamp_position = override_clamp

    # speed is 100
    # expected reflection speed = speed * 2 = 200
    action.execute("idle", 0.016)

    new_speed = math.sqrt(ball.vx**2 + ball.vy**2)
    assert new_speed > 150 # Roughly 200
    assert ball.hp == 100 # No boundary damage should be taken
