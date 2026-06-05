"""
Auto-generated tests for: Guardian
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_types_guardian import Guardian


def test_guardian_initialization():
    ball = Guardian(ball_id=1, x=100, y=200)
    assert ball.id == 1
    assert ball.hp == 180
    assert ball.max_hp == 180
    assert ball.alive is True
    assert ball.personality == "guardian"


def test_guardian_hp_percent():
    ball = Guardian(ball_id=1)
    ball.hp = 90
    assert abs(ball.get_hp_percent() - 90/180) < 0.01


def test_guardian_take_damage():
    ball = Guardian(ball_id=1)
    ball.take_damage(10)
    assert ball.hp == 170
    assert ball.alive is True
    ball.take_damage(280)
    assert ball.alive is False


def test_guardian_skill():
    ball = Guardian(ball_id=1)
    assert ball.use_skill() is True
    assert ball.skill_timer == 6.0
    assert ball.use_skill() is False


def test_guardian_actions():
    ball = Guardian(ball_id=1)
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
