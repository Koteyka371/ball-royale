"""
Auto-generated tests for: Berserker
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_types_berserker import Berserker


def test_berserker_initialization():
    ball = Berserker(ball_id=1, x=100, y=200)
    assert ball.id == 1
    assert ball.hp == 100
    assert ball.max_hp == 100
    assert ball.alive is True
    assert ball.personality == "berserker"


def test_berserker_hp_percent():
    ball = Berserker(ball_id=1)
    ball.hp = 50
    assert ball.get_hp_percent() == 0.5


def test_berserker_take_damage():
    ball = Berserker(ball_id=1)
    ball.take_damage(50)
    assert ball.hp == 50
    assert ball.alive is True
    ball.take_damage(100)
    assert ball.alive is False


def test_berserker_skill():
    ball = Berserker(ball_id=1)
    assert ball.use_skill() is True
    assert ball.skill_timer == 5.5
    assert ball.use_skill() is False


def test_berserker_actions():
    ball = Berserker(ball_id=1)
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
