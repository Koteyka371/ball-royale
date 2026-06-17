import pytest
from ai.ball_types_king import King

def test_king_initialization():
    b = King(ball_id=1, x=100.0, y=200.0)
    assert b.id == 1
    assert b.x == 100.0
    assert b.y == 200.0
    assert b.BALL_TYPE == "king"
    assert b.hp == 150
    assert b.max_hp == 150
    assert b.personality.character == "leader"

def test_king_hp_percent():
    b = King(1)
    assert b.get_hp_percent() == 1.0
    b.hp = 75
    assert b.get_hp_percent() == 0.5
    b.max_hp = 0
    assert b.get_hp_percent() == 0.0

def test_king_take_damage():
    b = King(1)
    b.take_damage(50)
    assert b.hp == 100
    assert b.alive is True
    assert b.first_hit_taken is True

    b.take_damage(100)
    assert b.hp <= 0
    assert b.alive is False

def test_king_skill():
    b = King(1)
    b.skill_timer = 0.0
    assert b.use_skill() is True
    assert b.skill_timer == 5.0
    assert b.use_skill() is False

def test_king_actions():
    b = King(1)
    b.flee(1.0)
    assert b.current_action == "flee"
    b.attack(1.0)
    assert b.current_action == "attack"
    b.defend(1.0)
    assert b.current_action == "defend"
    b.collect_booster(1.0)
    assert b.current_action == "opportunistic"
    b.idle(1.0)
    assert b.current_action == "idle"
