"""
Auto-generated tests for: Bomber
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_types_bomber import Bomber


def test_bomber_initialization():
    ball = Bomber(ball_id=1, x=100, y=200)
    assert ball.id == 1
    assert ball.hp == 60
    assert ball.max_hp == 60
    assert ball.alive is True
    assert ball.personality == "reckless"


def test_bomber_hp_percent():
    ball = Bomber(ball_id=1)
    ball.hp = 45
    assert abs(ball.get_hp_percent() - ball.hp / ball.max_hp) < 0.01


def test_bomber_take_damage():
    ball = Bomber(ball_id=1)
    ball.take_damage(10)
    assert ball.hp == 50
    assert ball.alive is True
    ball.take_damage(190)
    assert ball.alive is False


def test_bomber_skill():
    ball = Bomber(ball_id=1)
    assert ball.use_skill() is True
    assert ball.skill_timer == 7.0
    assert ball.use_skill() is False


def test_bomber_actions():
    ball = Bomber(ball_id=1)
    ball.flee(0.016)
    assert ball.current_action == "flee"
    ball.attack(0.016)
    assert ball.current_action == "attack"
    ball.defend(0.016)
    assert ball.current_action == "defend"
    ball.collect_booster(0.016)
    assert ball.current_action == "opportunistic"
    ball.idle(0.016)
    assert ball.current_action == "idle"


class MockTarget:
    def __init__(self, x, y, radius=10):
        self.x = x
        self.y = y
        self.radius = radius

def test_bomber_attack_moves_to_target():
    ball = Bomber(ball_id=1, x=0, y=0)
    target = MockTarget(x=100, y=0)
    ball.attack(delta=1.0, target=target)

    # Bomber speed is 4.0. Step = 4.0 * 1.0 * 60 = 240.
    # Dist is 100, so it should move max 100, meaning it arrives at target.
    assert ball.x > 0
    assert ball.current_action == "attack"

def test_bomber_attack_explode():
    ball = Bomber(ball_id=1, x=0, y=0)
    target = MockTarget(x=10, y=0)
    ball.skill_timer = 0

    ball.attack(delta=0.1, target=target)

    assert ball.hp == 0.0
    assert ball.alive is False
    assert ball.current_action == "explode"
