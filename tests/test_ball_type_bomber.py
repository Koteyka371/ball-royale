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
    assert ball.hp == 90
    assert ball.max_hp == 90
    assert ball.alive is True
    assert ball.personality == "reckless"


def test_bomber_hp_percent():
    ball = Bomber(ball_id=1)
    ball.hp = 45
    assert abs(ball.get_hp_percent() - 45/90) < 0.01


def test_bomber_take_damage():
    ball = Bomber(ball_id=1)
    ball.take_damage(10)
    assert ball.hp == 80
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
