import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_types_hard import Hard

def test_hard_initialization():
    ball = Hard(ball_id=1, x=100, y=200)
    assert ball.id == 1
    assert ball.hp == 150
    assert ball.max_hp == 150
    assert ball.SPEED == 3.5
    assert ball.DAMAGE == 20
    assert ball.RADIUS == 11
    assert ball.PERCEPTION_RADIUS == 300
    assert ball.AGGRESSION == 0.8
    assert ball.COLOR == "darkred"
    assert ball.SKILL == "perfect_strike"
    assert ball.SKILL_COOLDOWN == 4.0
    assert ball.difficulty == "hard"
    assert ball.BALL_TYPE == "hard"
    assert ball.alive is True

def test_hard_hp_percent():
    ball = Hard(ball_id=1)
    ball.hp = 75
    assert abs(ball.get_hp_percent() - 0.5) < 0.01

def test_hard_take_damage():
    ball = Hard(ball_id=1)
    ball.take_damage(50)
    assert ball.hp == 100
    assert ball.alive is True
    assert ball.first_hit_taken is True

    ball.take_damage(100)
    assert ball.hp == 0
    assert ball.alive is False

def test_hard_skill():
    ball = Hard(ball_id=1)
    assert ball.use_skill() is True
    assert ball.skill_timer == 4.0
    assert ball.use_skill() is False

def test_hard_actions():
    ball = Hard(ball_id=1)

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
