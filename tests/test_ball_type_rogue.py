"""
Auto-generated tests for: Rogue
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_types_rogue import Rogue


def test_rogue_initialization():
    ball = Rogue(ball_id=1, x=100, y=200)
    assert ball.id == 1
    assert ball.hp == 75
    assert ball.max_hp == 75
    assert ball.alive is True
    assert ball.personality.character == "cunning"


def test_rogue_hp_percent():
    ball = Rogue(ball_id=1)
    ball.hp = 37
    assert abs(ball.get_hp_percent() - 37/75) < 0.01


def test_rogue_take_damage():
    ball = Rogue(ball_id=1)
    ball.take_damage(10)
    assert ball.hp == 65
    assert ball.alive is True
    ball.take_damage(175)
    assert ball.alive is False


def test_rogue_skill():
    ball = Rogue(ball_id=1)
    assert ball.use_skill() is True
    assert ball.skill_timer == 4.5
    assert ball.use_skill() is False


def test_rogue_actions():
    ball = Rogue(ball_id=1)
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
