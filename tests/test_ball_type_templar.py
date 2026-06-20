"""
Auto-generated tests for: Templar
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_types_templar import Templar


def test_templar_initialization():
    ball = Templar(ball_id=1, x=100, y=200)
    assert ball.id == 1
    assert ball.hp == 170
    assert ball.max_hp == 170
    assert ball.alive is True


def test_templar_hp_percent():
    ball = Templar(ball_id=1)
    ball.hp = 170 / 2
    assert abs(ball.get_hp_percent() - 0.5) < 0.01


def test_templar_take_damage():
    ball = Templar(ball_id=1)
    ball.take_damage(10)
    assert ball.hp == 170 - 10
    assert ball.alive is True
    ball.take_damage(170)
    assert ball.alive is False


def test_templar_skill():
    ball = Templar(ball_id=1)
    assert ball.use_skill() is True
    assert ball.skill_timer == 5.5
    assert ball.use_skill() is False


def test_templar_actions():
    ball = Templar(ball_id=1)
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
