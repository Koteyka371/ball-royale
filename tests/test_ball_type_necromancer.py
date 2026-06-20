"""
Auto-generated tests for: Necromancer
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_types_necromancer import Necromancer


def test_necromancer_initialization():
    ball = Necromancer(ball_id=1, x=100, y=200)
    assert ball.id == 1
    assert ball.hp == 90
    assert ball.max_hp == 90
    assert ball.alive is True


def test_necromancer_hp_percent():
    ball = Necromancer(ball_id=1)
    ball.hp = 90 / 2
    assert abs(ball.get_hp_percent() - 0.5) < 0.01


def test_necromancer_take_damage():
    ball = Necromancer(ball_id=1)
    ball.take_damage(10)
    assert ball.hp == 90 - 10
    assert ball.alive is True
    ball.take_damage(90)
    assert ball.alive is False


def test_necromancer_skill():
    ball = Necromancer(ball_id=1)
    assert ball.use_skill() is True
    assert ball.skill_timer == 8.0
    assert ball.use_skill() is False


def test_necromancer_actions():
    ball = Necromancer(ball_id=1)
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
