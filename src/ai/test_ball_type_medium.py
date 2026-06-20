import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.ball_types_medium import Medium

def test_medium_initialization():
    ball = Medium(ball_id=1, x=100, y=200)
    assert ball.id == 1
    assert ball.hp == 100
    assert ball.max_hp == 100
    assert ball.alive is True
    assert ball.difficulty == "medium"
    assert ball.BALL_TYPE == "medium"

def test_medium_hp_percent():
    ball = Medium(ball_id=1)
    ball.hp = 50
    assert abs(ball.get_hp_percent() - ball.hp / ball.max_hp) < 0.01

def test_medium_take_damage():
    ball = Medium(ball_id=1)
    ball.take_damage(20)
    assert ball.hp == 80
    assert ball.alive is True
    ball.take_damage(100)
    assert ball.alive is False

def test_medium_skill():
    ball = Medium(ball_id=1)
    assert ball.use_skill() is True
    assert ball.skill_timer == 8.0
    assert ball.use_skill() is False

def test_medium_actions():
    ball = Medium(ball_id=1)
    ball.flee(0.016)
    assert ball.current_action == "flee"
    ball.attack(0.016)
    assert ball.current_action == "attack"
    ball.defend(0.016)
    assert ball.current_action == "defend"
    ball.collect_booster(0.016)
    assert ball.current_action == "collect_booster"
    ball.idle(0.016)
    assert ball.current_action == "idle"
