import pytest
from ai.action import Action
import math

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.width = 1000
        self.height = 1000
        self.balls = []
        self.items = []
        self.events = []

class MockHazard:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 15.0

class MockBall:
    def __init__(self, x, y, vx=0, vy=0, skill="grapple"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.skill = skill
        self.skill_cooldown = 5.0
        self.skill_timer = 0.0
        self.alive = True
        self.team = 1
        self.id = 1
        self.hp = 100

def test_grapple_swing_wall_speed_boost():
    world = MockWorld()
    ball = MockBall(100, 500, vx=10, vy=0)
    world.balls.append(ball)

    action = Action(ball, world)
    action._use_skill()

    # No longer pulled to wall when swinging!
    assert ball.x == 100.0
    assert ball.y == 500.0

    # Check speed boost (since wall is on left/right, boost is along y axis)
    assert ball.vx == 10.0
    assert ball.vy == 100.0  # Boosted because vy was >= 0

def test_grapple_swing_hazard_speed_boost():
    world = MockWorld()
    # Traveling right
    ball = MockBall(500, 500, vx=10, vy=0)
    world.balls.append(ball)

    # Hazard is down and right
    node = MockHazard(600, 600, "grapple_node")
    world.arena.hazards.append(node)

    action = Action(ball, world)
    action._use_skill()

    # No longer pulled to hazard!
    assert ball.x == 500.0
    assert ball.y == 500.0

    # Check speed boost. The vector from ball to hazard is (100, 100).
    # Tangents are (-100, 100) and (100, -100).
    # Current velocity is (10, 0).
    # Dot with (-100, 100) is -1000. Dot with (100, -100) is +1000.
    # So we pick (100, -100), normalized is (0.707, -0.707).
    # We add this * 100 to the current velocity.
    assert ball.vx > 10.0
    assert ball.vy < 0.0
