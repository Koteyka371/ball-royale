"""
Auto-generated tests for: Scout
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_types_scout import Scout


def test_scout_initialization():
    ball = Scout(ball_id=1, x=100, y=200)
    assert ball.id == 1
    assert ball.hp == 80
    assert ball.max_hp == 80
    assert ball.alive is True
    assert ball.personality == "scout"


def test_scout_hp_percent():
    ball = Scout(ball_id=1)
    ball.hp = 40
    assert abs(ball.get_hp_percent() - 40/80) < 0.01


def test_scout_take_damage():
    ball = Scout(ball_id=1)
    ball.take_damage(10)
    assert ball.hp == 70
    assert ball.alive is True
    ball.take_damage(180)
    assert ball.alive is False


def test_scout_skill():
    ball = Scout(ball_id=1)
    assert ball.use_skill() is True
    assert ball.skill_timer == 3.5
    assert ball.use_skill() is False


def test_scout_actions():
    ball = Scout(ball_id=1)
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
