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

class MockBall:
    def __init__(self, x, y, skill="tunnel"):
        self.x = x
        self.y = y
        self.skill = skill
        self.skill_cooldown = 15.0
        self.skill_timer = 0.0
        self.alive = True
        self.team = 1
        self.id = 1
        self.hp = 100
        self.radius = 10.0
        self.intangible = False
        self.intangible_timer = 0.0

class MockHazard:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.is_disabled_by_flare = False
        self.kind = "hazard"

def test_tunnel_wall():
    world = MockWorld()
    ball = MockBall(500, 500)
    world.balls.append(ball)

    # left wall
    ball.x = 5
    ball.y = 500

    action = Action(ball, world)
    action._use_skill()

    assert ball.x == 65
    assert ball.y == 500
    assert ball.intangible == True
    assert ball.intangible_timer == 0.5
    assert ball.skill_timer == 15.0

    # reset and try hazard
    ball.intangible = False
    ball.intangible_timer = 0.0
    ball.skill_timer = 0.0

    ball.x = 500
    ball.y = 500
    world.arena.hazards.append(MockHazard(520, 500, 20.0))
    action._use_skill()

    # distance is 20, threshold is 10 + 15 = 25, hazard radius is 20 -> dist_sq <= 45^2
    assert ball.x > 500 # Should be teleported to the other side
    assert ball.y == 500
    assert ball.intangible == True
    assert ball.intangible_timer == 0.5
    assert ball.skill_timer == 15.0

    # The new position should be 520 + nx * (20 + 10 + 5) = 520 + 1 * 35 = 555
    assert math.isclose(ball.x, 555.0)
