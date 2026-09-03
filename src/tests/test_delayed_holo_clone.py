import pytest
import sys
import copy
sys.path.append("src")
from ai.action import Action

class MockEnemy:
    def __init__(self):
        self.id = "e1"
        self.x = 100.0
        self.y = 100.0
        self.hp = 100.0
        self.alive = True
        self.nemesis_shield_active = False

class MockBall:
    def __init__(self):
        self.id = "b1"
        self.x = 0.0
        self.y = 0.0
        self.damage = 10.0
        self.ball_type = "base"
        self.is_hologram = False

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []

    def _deal_damage(self, attacker, target):
        target.hp -= getattr(attacker, "damage", 10.0)

def test_delayed_holo_clone():
    world = MockWorld()
    ball = MockBall()
    enemy = MockEnemy()
    world.balls = [ball, enemy]

    action = Action(ball, world)

    assert getattr(ball, "delayed_clones", []) == []

    # Attempt damage
    action._attempt_damage(ball, enemy)

    assert len(getattr(ball, "delayed_clones", [])) == 1
    clone_data = ball.delayed_clones[0]
    assert clone_data["timer"] == 1.0
    assert clone_data["x"] == 0.0
    assert clone_data["y"] == 0.0

    # Tick before time
    action.execute("attack", 0.5)
    assert len(ball.delayed_clones) == 1
    assert ball.delayed_clones[0]["timer"] == 0.5
    assert len(world.balls) == 2

    # Tick past time
    action.execute("attack", 0.6)

    assert len(getattr(ball, "delayed_clones", [])) == 0
    assert len(world.balls) == 3 # The clone is added
    clone = world.balls[-1]

    assert getattr(clone, "is_hologram", False) is True
    assert getattr(clone, "hologram_timer", 0.0) == 0.5

    # verify attack happened
    # base dmg is 10, first attack dropped it to 90
    # second attack from clone should drop it to 80
    assert enemy.hp == 76.0 # 100 - (10.0 * 0.4) in this test, _attempt_damage doesn't call world._deal_damage as it assumes it is the 'internal' damage step where we check shields.
