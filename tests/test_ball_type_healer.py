"""
Auto-generated tests for: Healer
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_types_healer import Healer


def test_healer_initialization():
    ball = Healer(ball_id=1, x=100, y=200)
    assert ball.id == 1
    assert ball.hp == 100
    assert ball.max_hp == 100
    assert ball.alive is True
    assert ball.personality == "caring"


def test_healer_hp_percent():
    ball = Healer(ball_id=1)
    ball.hp = 60
    assert abs(ball.get_hp_percent() - ball.hp / ball.max_hp) < 0.01


def test_healer_take_damage():
    ball = Healer(ball_id=1)
    ball.take_damage(20)
    assert ball.hp == 80
    assert ball.alive is True
    ball.take_damage(180)
    assert ball.alive is False


def test_healer_skill():
    ball = Healer(ball_id=1)
    assert ball.use_skill() is True
    assert ball.skill_timer == 2.5
    assert ball.use_skill() is False


def test_healer_actions():
    ball = Healer(ball_id=1)
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

def test_healer_heal_ally():
    ball = Healer(ball_id=1, x=0, y=0)
    class DummyAlly:
        def __init__(self):
            self.x = 0
            self.y = 500
            self.hp = 50
            self.max_hp = 100
            self.radius = 10
    ally = DummyAlly()

    # Healer should move towards the ally because distance (100) > attack_range (10 + 10 + 5 = 25)
    ball.heal_ally(1.0, ally)

    assert ball.current_action == "defend"
    assert ball.y > 0  # Should have moved towards the ally (y=100)
    assert ally.hp == 50  # Out of range, should not heal

    # Move ally close
    ally.y = ball.y + 15

    # Reset cooldowns just in case
    ball.attack_timer = 0.0
    ball.skill_timer = 0.0

    ball.heal_ally(1.0, ally)
    assert ally.hp == 50 + (ball.DAMAGE * 3.0)
    assert ball.attack_timer > 0
    assert ball.skill_timer == ball.SKILL_COOLDOWN
