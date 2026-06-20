"""
Auto-generated tests for: Paladin
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_types_paladin import Paladin


def test_paladin_initialization():
    ball = Paladin(ball_id=1, x=100, y=200)
    assert ball.id == 1
    assert ball.hp == 180
    assert ball.max_hp == 180
    assert ball.alive is True


def test_paladin_hp_percent():
    ball = Paladin(ball_id=1)
    ball.hp = 180 / 2
    assert abs(ball.get_hp_percent() - 0.5) < 0.01


def test_paladin_take_damage():
    ball = Paladin(ball_id=1)
    ball.take_damage(10)
    assert ball.hp == 180 - 10
    assert ball.alive is True
    ball.take_damage(180)
    assert ball.alive is False


def test_paladin_skill():
    ball = Paladin(ball_id=1)
    assert ball.use_skill() is True
    assert ball.skill_timer == 6.0
    assert ball.use_skill() is False


def test_paladin_actions():
    ball = Paladin(ball_id=1)
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
