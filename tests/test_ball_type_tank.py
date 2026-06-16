"""
Auto-generated tests for: Tank
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_types_tank import Tank


def test_tank_initialization():
    ball = Tank(ball_id=1, x=100, y=200)
    assert ball.id == 1
    assert ball.hp == 200
    assert ball.max_hp == 200
    assert ball.alive is True
    assert ball.personality == "supportive"


def test_tank_hp_percent():
    ball = Tank(ball_id=1)
    ball.hp = 100
    assert abs(ball.get_hp_percent() - 100/200) < 0.01


def test_tank_take_damage():
    ball = Tank(ball_id=1)
    ball.take_damage(10)
    assert ball.hp == 190
    assert ball.alive is True
    ball.take_damage(300)
    assert ball.alive is False


def test_tank_skill():
    ball = Tank(ball_id=1)
    assert ball.use_skill() is True
    assert ball.skill_timer == 8.0
    assert ball.use_skill() is False


def test_tank_actions():
    ball = Tank(ball_id=1)
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
