import pytest
from ai.new_ball_magnet import Magnet

def test_magnet_initialization():
    m = Magnet(1, 10, 20)
    assert m.id == 1
    assert m.x == 10
    assert m.y == 20
    assert m.hp == Magnet.HP
    assert m.max_hp == Magnet.HP
    assert m.alive is True
    assert m.kills == 0
    assert m.skill_timer == 0.0

def test_magnet_hp_percent():
    m = Magnet(1)
    m.hp = 75
    m.max_hp = 150
    assert m.get_hp_percent() == 0.5

def test_magnet_take_damage():
    m = Magnet(1)
    m.take_damage(50)
    assert m.hp == 100
    assert m.first_hit_taken is True

    m.take_damage(100)
    assert m.hp == 0
    assert m.alive is False

def test_magnet_skill():
    m = Magnet(1)
    assert m.use_skill() is True
    assert m.skill_timer == Magnet.SKILL_COOLDOWN
    assert m.use_skill() is False

def test_magnet_actions():
    m = Magnet(1)
    m.flee(0.1)
    assert m.current_action == "flee"
    m.attack(0.1)
    assert m.current_action == "attack"
    m.defend(0.1)
    assert m.current_action == "defend"
    m.collect_booster(0.1)
    assert m.current_action == "opportunistic"
    m.idle(0.1)
    assert m.current_action == "idle"
