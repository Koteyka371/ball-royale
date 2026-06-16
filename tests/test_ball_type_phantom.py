"""
Auto-generated tests for: Phantom
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_types_phantom import Phantom


def test_phantom_initialization():
    ball = Phantom(ball_id=1, x=100, y=200)
    assert ball.id == 1
    assert ball.hp == 65
    assert ball.max_hp == 65
    assert ball.alive is True
    assert ball.personality == "cunning"


def test_phantom_hp_percent():
    ball = Phantom(ball_id=1)
    ball.hp = 32
    assert abs(ball.get_hp_percent() - 32/65) < 0.01


def test_phantom_take_damage():
    ball = Phantom(ball_id=1)
    ball.take_damage(10)
    assert ball.hp == 55
    assert ball.alive is True
    ball.take_damage(165)
    assert ball.alive is False


def test_phantom_skill():
    ball = Phantom(ball_id=1)
    assert ball.use_skill() is True
    assert ball.skill_timer == 4.0
    assert ball.use_skill() is False


def test_phantom_actions():
    ball = Phantom(ball_id=1)
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
