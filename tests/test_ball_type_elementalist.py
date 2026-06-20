"""
Auto-generated tests for: Elementalist
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_types_elementalist import Elementalist


def test_elementalist_initialization():
    ball = Elementalist(ball_id=1, x=100, y=200)
    assert ball.id == 1
    assert ball.hp == 95
    assert ball.max_hp == 95
    assert ball.alive is True


def test_elementalist_hp_percent():
    ball = Elementalist(ball_id=1)
    ball.hp = 95 / 2
    assert abs(ball.get_hp_percent() - 0.5) < 0.01


def test_elementalist_take_damage():
    ball = Elementalist(ball_id=1)
    ball.take_damage(10)
    assert ball.hp == 95 - 10
    assert ball.alive is True
    ball.take_damage(95)
    assert ball.alive is False


def test_elementalist_skill():
    ball = Elementalist(ball_id=1)
    assert ball.use_skill() is True
    assert ball.skill_timer == 5.0
    assert ball.use_skill() is False


def test_elementalist_actions():
    ball = Elementalist(ball_id=1)
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
