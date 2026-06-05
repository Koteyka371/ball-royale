"""
Auto-generated tests for: Sniper
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_types_sniper import Sniper


def test_sniper_initialization():
    ball = Sniper(ball_id=1, x=100, y=200)
    assert ball.id == 1
    assert ball.hp == 60
    assert ball.max_hp == 60
    assert ball.alive is True
    assert ball.personality == "sniper"


def test_sniper_hp_percent():
    ball = Sniper(ball_id=1)
    ball.hp = 30
    assert ball.get_hp_percent() == 0.5


def test_sniper_take_damage():
    ball = Sniper(ball_id=1)
    ball.take_damage(50)
    assert ball.hp == 10
    assert ball.alive is True
    ball.take_damage(60)
    assert ball.alive is False


def test_sniper_skill():
    ball = Sniper(ball_id=1)
    assert ball.use_skill() is True
    assert ball.skill_timer == 6.0
    assert ball.use_skill() is False


def test_sniper_actions():
    ball = Sniper(ball_id=1)
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
