"""
Auto-generated tests for: Ninja
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_types_ninja import Ninja

def test_ninja_initialization():
    ball = Ninja(ball_id=1, x=100, y=200)
    assert ball.id == 1
    assert ball.x == 100
    assert ball.y == 200
    assert ball.hp == Ninja.HP
    assert ball.max_hp == Ninja.HP
    assert ball.BALL_TYPE == "ninja"

def test_ninja_hp_percent():
    ball = Ninja(ball_id=1)
    assert ball.get_hp_percent() == 1.0
    ball.take_damage(ball.max_hp / 2)
    assert ball.get_hp_percent() == 0.5

def test_ninja_take_damage():
    ball = Ninja(ball_id=1)
    ball.take_damage(10)
    assert ball.hp == Ninja.HP - 10
    assert ball.alive is True

    ball.take_damage(Ninja.HP)
    assert ball.hp <= 0
    assert ball.alive is False

def test_ninja_skill():
    ball = Ninja(ball_id=1)
    assert ball.use_skill() is True
    assert ball.use_skill() is False  # Cooldown active

    ball.skill_timer = 0
    assert ball.use_skill() is True

def test_ninja_actions():
    ball = Ninja(ball_id=1)

    ball.flee(1.0)
    assert ball.current_action == "flee"

    ball.attack(1.0)
    assert ball.current_action == "attack"

    ball.defend(1.0)
    assert ball.current_action == "defend"

    ball.collect_booster(1.0)
    assert ball.current_action == "opportunistic"
