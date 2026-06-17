"""
Auto-generated tests for: Spectator
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_types_spectator import Spectator


def test_spectator_initialization():
    ball = Spectator(ball_id=1, x=100, y=200)
    assert ball.id == 1
    assert ball.hp == 99999
    assert ball.max_hp == 99999
    assert ball.alive is True
    assert ball.personality == "spectator"


def test_spectator_hp_percent():
    ball = Spectator(ball_id=1)
    ball.hp = 49999
    assert abs(ball.get_hp_percent() - 49999/99999) < 0.01


def test_spectator_take_damage():
    ball = Spectator(ball_id=1)
    ball.take_damage(10)
    assert ball.hp == 99989
    assert ball.alive is True
    ball.take_damage(100099)
    assert ball.alive is False


def test_spectator_skill():
    ball = Spectator(ball_id=1)
    assert ball.use_skill() is True
    assert ball.skill_timer == 1.0
    assert ball.use_skill() is False


def test_spectator_actions():
    ball = Spectator(ball_id=1)
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
