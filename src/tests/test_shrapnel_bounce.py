import pytest
import math
from ai.action import Action

class MockBall:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.radius = 10
        self.hp = 100
        self.id = 1
        self.team = 1
        self.is_blinded = False
        self.memory = {}
    def take_damage(self, dmg):
        self.hp -= dmg

class MockArena:
    def __init__(self):
        self.hazards = []
    def clamp_position(self, x, y, radius):
        bounced = False
        if x < radius: x = radius; bounced = True
        if x > 100 - radius: x = 100 - radius; bounced = True
        if y < radius: y = radius; bounced = True
        if y > 100 - radius: y = 100 - radius; bounced = True
        return x, y, bounced

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []
    def _deal_damage(self, target, source):
        pass
    def broadcast_event(self, event):
        pass

class Shrapnel:
    def __init__(self):
        self.kind = "shrapnel"
        self.x = 8
        self.y = 8
        self.vx = -100
        self.vy = -100
        self.radius = 5
        self.duration = 5.0
        self.damage = 10.0

def test_shrapnel_bounce_x_and_y():
    ball = MockBall()
    world = MockWorld()
    world.balls.append(ball)

    shrapnel = Shrapnel()
    world.arena.hazards.append(shrapnel)

    action = Action(ball, world)

    # Delta of 0.1 means movement by -10 in x and y.
    # Current pos: 8, 8. Expected new pos: -2, -2.
    # Radius is 5.
    # The clamp should happen at x=5, y=5.
    # Because x != 5 (it's -2), vx reverses.
    # Because y != 5 (it's -2), vy reverses.
    # Then velocity gets damped by (1.0 - 2.0 * delta) = 0.8
    # Original vx: -100. Reversed: 100. Damped: 80.
    action.execute({}, 0.1)

    assert shrapnel.x == 5
    assert shrapnel.y == 5
    assert math.isclose(shrapnel.vx, 80.0)
    assert math.isclose(shrapnel.vy, 80.0)
