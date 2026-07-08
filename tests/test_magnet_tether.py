
import pytest
from ai.action import Action

class MockBall:
    def __init__(self, x, y, team):
        self.x = x
        self.y = y
        self.team = team
        self.radius = 10.0
        self.traits = []
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.speed = 100.0
        self.base_speed = 100.0
        self.alive = True
        self.id = id(self)
        self.ball_type = "default"
        self.skill = "magnet_tether"

class MockWorld:
    def __init__(self):
        self.balls = []
        self.game_mode = {}

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [b for b in self.balls if b != ball and b.team != ball.team], "allies": []}

def test_magnet_tether():
    world = MockWorld()
    b1 = MockBall(0, 0, 1)
    b2 = MockBall(100, 0, 2)
    world.balls = [b1, b2]

    action = Action(b1, world)

    # Trigger magnet tether
    action.execute("use_skill", 1.0)

    assert hasattr(b1, "magnet_tether_timer")
    assert hasattr(b1, "magnet_tether_target")
    assert b1.magnet_tether_target == b2

    # Movement should occur
    action.execute("idle", 0.1) # Simulate one frame

    # Since it's pulled, b1.x should increase towards b2.x
    assert b1.x > 0

def test_magnet_tether_grapple_wall():
    world = MockWorld()
    world.arena = type("Arena", (), {"width": 1000.0, "height": 1000.0})()
    b1 = MockBall(10, 500, 1) # Close to left wall (x=0)
    world.balls = [b1] # No enemies

    action = Action(b1, world)

    # Trigger magnet tether
    action.execute("use_skill", 1.0)

    assert hasattr(b1, "magnet_tether_timer")
    assert hasattr(b1, "magnet_tether_target")

    target = b1.magnet_tether_target
    assert target.x == 0.0
    assert target.y == 500
    assert getattr(target, "alive", False) == True

    # Movement should occur
    action.execute("idle", 0.1) # Simulate one frame

    # Since it's pulled towards x=0, b1.x should decrease
    assert b1.x < 10
