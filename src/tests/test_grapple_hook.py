import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.action import Action
import math

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

class MockBall:
    def __init__(self, x, y, team, id):
        self.x = x
        self.y = y
        self.team = team
        self.id = id
        self.vx = 0.0
        self.vy = 0.0
        self.skill = "grapple_hook"
        self.active_skill = "grapple_hook"
        self.SKILL_COOLDOWN = 5.0
        self.skill_timer = 0.0
        self.hp = 100
        self.alive = True
        self.state_history = []
        self.charge_level = 100

def test_grapple_hook():
    world = MockWorld()
    hazard = MockBall(x=800, y=800, team="Hazard", id="h1")
    hazard.kind = "hazard"
    world.arena.hazards = [hazard]

    ball = MockBall(x=500, y=500, team="Team A", id="b1")

    action = Action(ball, world)
    action._use_skill()

    assert ball.skill_timer > 0.0
    # The hazard is at (800, 800) which is dist_sq = 90000 + 90000 = 180000 (valid, < 250000)
    # Wall dist is min(500, 500, 500, 500) = 500. sq = 250000.
    # Hazard is closer than wall. So it grapples to hazard.
    assert ball.vx > 0
    assert ball.vy > 0
    assert math.isclose(ball.vx, ball.vy)

    # Test wall grapple
    ball2 = MockBall(x=100, y=500, team="Team A", id="b2")

    action2 = Action(ball2, world)
    action2._use_skill()

    assert ball2.skill_timer > 0.0
    assert ball2.vx < 0 # Grapples left


def test_out_of_bounds():
    world = MockWorld()

    # Test out of bounds on left
    ball = MockBall(x=-100, y=500, team="Team A", id="b1")
    action = Action(ball, world)
    action._use_skill()

    # If the ball is at x=-100, the left wall is at x=0. The dx will be 0 - (-100) = +100
    # The ball should be pulled to the right (vx > 0)
    assert ball.vx > 0
