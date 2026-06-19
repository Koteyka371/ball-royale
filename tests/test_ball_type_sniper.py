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
    assert ball.hp == 70
    assert ball.max_hp == 70
    assert ball.alive is True
    assert ball.personality == "cautious"


def test_sniper_hp_percent():
    ball = Sniper(ball_id=1)
    ball.hp = 30
    assert abs(ball.get_hp_percent() - ball.hp / ball.max_hp) < 0.01


def test_sniper_take_damage():
    ball = Sniper(ball_id=1)
    ball.take_damage(10)
    assert ball.hp == 60
    assert ball.alive is True
    ball.take_damage(160)
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
    assert ball.current_action == "kite"
    ball.kite(0.016)
    assert ball.current_action == "kite"
    ball.defend(0.016)
    assert ball.current_action == "defend"
    ball.collect_booster(0.016)
    assert ball.current_action == "opportunistic"
    ball.idle(0.016)
    assert ball.current_action == "idle"

class MockTarget:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def test_sniper_kite_keep_distance():
    ball = Sniper(ball_id=1, x=100.0, y=100.0)
    target = MockTarget(100.0, 300.0) # dist = 200, attack_range = 150
    # Expected to move closer
    ball.kite(0.1, target)
    assert ball.current_action == "kite"
    assert ball.y > 100.0

def test_sniper_kite_retreat():
    ball = Sniper(ball_id=1, x=100.0, y=100.0)
    target = MockTarget(100.0, 200.0) # dist = 100, < 150 * 0.8 (120)
    # Expected to move away
    ball.kite(0.1, target)
    assert ball.y < 100.0

def test_sniper_kite_use_skill():
    ball = Sniper(ball_id=1, x=100.0, y=100.0)
    target = MockTarget(100.0, 200.0) # dist = 100
    ball.skill_timer = 0.0
    ball.kite(0.1, target)
    assert ball.skill_timer > 0.0
