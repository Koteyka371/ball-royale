"""
Auto-generated tests for: Healer
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_types_healer import Healer


def test_healer_initialization():
    ball = Healer(ball_id=1, x=100, y=200)
    assert ball.id == 1
    assert ball.hp == 80
    assert ball.max_hp == 80
    assert ball.alive is True
    assert ball.personality.character == "supportive"


def test_healer_hp_percent():
    ball = Healer(ball_id=1)
    ball.hp = 40
    assert abs(ball.get_hp_percent() - 40/80) < 0.01


def test_healer_take_damage():
    ball = Healer(ball_id=1)
    ball.take_damage(10)
    assert ball.hp == 70
    assert ball.alive is True
    ball.take_damage(180)
    assert ball.alive is False


def test_healer_skill():
    ball = Healer(ball_id=1)
    assert ball.use_skill() is True
    assert ball.skill_timer == 4.0
    assert ball.use_skill() is False


def test_healer_actions():
    ball = Healer(ball_id=1)
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
