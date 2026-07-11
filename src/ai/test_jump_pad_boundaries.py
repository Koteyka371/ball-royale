import pytest
import math
from ai.action import Action
from ai.game_modes import JumpPadBoundariesMode

class MockArena:
    def __init__(self):
        self.hazards = []
        self.boundary_states = {}

    def clamp_position(self, x, y, r):
        bounced = False
        if x < r:
            x = r
            bounced = True
        elif x > 1000 - r:
            x = 1000 - r
            bounced = True
        if y < r:
            y = r
            bounced = True
        elif y > 1000 - r:
            y = 1000 - r
            bounced = True
        return x, y, bounced

class MockWorld:
    def __init__(self, width=1000, height=1000):
        self.width = width
        self.height = height
        self.game_mode = JumpPadBoundariesMode()
        self.arena = MockArena()
        self.events = []

    def get_nearby_entities(self, ball, r):
        return {"enemies": [], "allies": [], "boosters": [], "items": [], "hazards": []}

class MockBall:
    def __init__(self, ball_type="base"):
        self.id = 1
        self.x = 10
        self.y = 500
        self.vx = -1000
        self.vy = 0
        self.hp = 100
        self.alive = True
        self.radius = 15
        self.team = "test"
        self.ball_type = ball_type
        self.speed = 100
        self.intangible = False
        self.intangible_timer = 0.0

def test_jump_pad_boundaries():
    world = MockWorld()
    ball = MockBall(ball_type="warrior")
    action = Action(ball, world)

    ball.x = -100
    action.execute("idle", 1.0)

    # Should not take damage
    assert ball.hp == 100

    speed = math.sqrt(ball.vx**2 + ball.vy**2)
    # New speed should be min(max(1000, 500) * 4.0, 6000.0) -> 4000.0
    assert math.isclose(speed, 4000.0, rel_tol=0.1)

    # Check that it is moving towards the center (vx > 0)
    assert ball.vx > 0
