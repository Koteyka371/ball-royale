import pytest
from ai.ball_types_avenger import Avenger

def test_avenger_initialization():
    ball = Avenger(ball_id=1, x=100, y=200)

    assert ball.id == 1
    assert ball.BALL_TYPE == "avenger"
    assert ball.x == 100
    assert ball.y == 200
    assert ball.hp == 120
    assert ball.max_hp == 120
    assert ball.damage == 10
    assert ball.speed == 2.0
    assert ball.alive is True
    assert ball.SKILL == "nemesis_pull"
    assert ball.SKILL_COOLDOWN == 8.0

def test_avenger_take_damage():
    ball = Avenger(ball_id=1)

    ball.take_damage(20)
    assert ball.hp == 100
    assert ball.first_hit_taken is True

def test_avenger_death():
    ball = Avenger(ball_id=1)

    ball.take_damage(120)
    assert ball.hp == 0
    assert ball.alive is False

def test_avenger_use_skill():
    ball = Avenger(ball_id=1)

    # Skill timer starts at 0, should be able to use skill
    assert ball.use_skill() is True
    assert ball.skill_timer == 8.0

    # Still on cooldown
    assert ball.use_skill() is False

def test_avenger_actions():
    ball = Avenger(ball_id=1)

    ball.attack(1.0)
    assert ball.current_action == "attack"

    ball.flee(1.0)
    assert ball.current_action == "flee"

    ball.idle(1.0)
    assert ball.current_action == "idle"
