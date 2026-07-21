import pytest
from ai.action import Action
class DummyWorld:
    def __init__(self):
        self.arena = DummyArena()
        self.tick = 0
    def _deal_damage(self, hazard, target, damage):
        target.hp -= damage
class DummyArena:
    def __init__(self):
        self.hazards = []
class DummyHazard:
    def __init__(self):
        self.kind = "phantom_grabber"
        self.x = 0
        self.y = 0
        self.radius = 50.0
        self.damage = 10.0
        self.invisible = True
        self.state = 0
        self.timer = 0.5
class DummyBall:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.hp = 100
        self.speed = 100
        self.stun_timer = 0.0
        self.speed_multiplier = 1.0

def test_phantom_grabber_invisible():
    world = DummyWorld()
    ball = DummyBall()
    action = Action(ball, world)
    hazard = DummyHazard()
    world.arena.hazards.append(hazard)
    action.execute("idle", 0.1)
    assert hazard.invisible is True
    assert ball.hp == 100
    assert ball.speed == 100

def test_phantom_grabber_visible_grab():
    world = DummyWorld()
    world.tick = 1
    ball = DummyBall()
    action = Action(ball, world)
    hazard = DummyHazard()
    hazard.state = 2 # grabbing
    hazard.timer = 1.0
    world.arena.hazards.append(hazard)
    action.execute("idle", 0.1)
    # Speed multiplier is changed instead of speed
    assert ball.speed_multiplier == 0.0
    assert ball.hp < 100
