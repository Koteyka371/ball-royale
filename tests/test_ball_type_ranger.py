"""
Auto-generated tests for: Ranger
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_types_ranger import Ranger


def test_ranger_initialization():
    ball = Ranger(ball_id=1, x=100, y=200)
    assert ball.id == 1
    assert ball.hp == 105
    assert ball.max_hp == 105
    assert ball.alive is True


def test_ranger_hp_percent():
    ball = Ranger(ball_id=1)
    ball.hp = 105 / 2
    assert abs(ball.get_hp_percent() - 0.5) < 0.01


def test_ranger_take_damage():
    ball = Ranger(ball_id=1)
    ball.take_damage(10)
    assert ball.hp == 105 - 10
    assert ball.alive is True
    ball.take_damage(105)
    assert ball.alive is False


def test_ranger_skill():
    ball = Ranger(ball_id=1)
    assert ball.use_skill() is True
    assert ball.skill_timer == 4.5
    assert ball.use_skill() is False


def test_ranger_actions():
    ball = Ranger(ball_id=1)
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

class MockTarget:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def test_ranger_kite_keep_distance():
    ball = Ranger(ball_id=1, x=100.0, y=100.0)
    target = MockTarget(100.0, 300.0) # dist = 200, attack_range = 50
    # Expected to move closer
    ball.kite(0.1, target)
    assert ball.current_action == "kite"
    assert ball.y > 100.0

def test_ranger_kite_retreat():
    ball = Ranger(ball_id=1, x=100.0, y=100.0)
    target = MockTarget(100.0, 130.0) # dist = 30, < 50 * 0.8 (40)
    # Expected to move away
    ball.kite(0.1, target)
    assert ball.y < 100.0

def test_ranger_kite_use_skill():
    ball = Ranger(ball_id=1, x=100.0, y=100.0)
    target = MockTarget(100.0, 140.0) # dist = 40
    ball.skill_timer = 0.0
    ball.kite(0.1, target)
    assert ball.skill_timer > 0.0
