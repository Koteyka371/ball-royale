"""
Auto-generated tests for: Warrior
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_types_warrior import Warrior


def test_warrior_initialization():
    ball = Warrior(ball_id=1, x=100, y=200)
    assert ball.id == 1
    assert ball.hp == 150
    assert ball.max_hp == 150
    assert ball.alive is True
    assert ball.personality == "aggressive"


def test_warrior_hp_percent():
    ball = Warrior(ball_id=1)
    ball.hp = 60
    assert abs(ball.get_hp_percent() - ball.hp / ball.max_hp) < 0.01


def test_warrior_take_damage():
    ball = Warrior(ball_id=1)
    ball.take_damage(10)
    assert ball.hp == 140
    assert ball.alive is True
    ball.take_damage(220)
    assert ball.alive is False


def test_warrior_skill():
    ball = Warrior(ball_id=1)
    assert ball.use_skill() is True
    assert ball.skill_timer == 5.0
    assert ball.use_skill() is False


def test_warrior_actions():
    ball = Warrior(ball_id=1)
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
