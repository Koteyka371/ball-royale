"""
Auto-generated tests for: Swarm
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_types_swarm import Swarm


def test_swarm_initialization():
    ball = Swarm(ball_id=1, x=100, y=200)
    assert ball.id == 1
    assert ball.hp == 60
    assert ball.max_hp == 60
    assert ball.alive is True
    assert ball.personality == "aggressive"


def test_swarm_hp_percent():
    ball = Swarm(ball_id=1)
    ball.hp = 30
    assert abs(ball.get_hp_percent() - 30/60) < 0.01


def test_swarm_take_damage():
    ball = Swarm(ball_id=1)
    ball.take_damage(10)
    assert ball.hp == 50
    assert ball.alive is True
    ball.take_damage(140)
    assert ball.alive is False


def test_swarm_skill():
    ball = Swarm(ball_id=1)
    assert ball.use_skill() is True
    assert ball.skill_timer == 6.0
    assert ball.use_skill() is False


def test_swarm_actions():
    ball = Swarm(ball_id=1)
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
