import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from ai.ball_types_engineer import Engineer

def test_engineer_initialization():
    b = Engineer(1, 10.0, 20.0)
    assert b.id == 1
    assert b.hp == 100
    assert b.BALL_TYPE == "engineer"
    assert b.alive is True

def test_engineer_take_damage():
    b = Engineer(1)
    b.take_damage(50)
    assert b.hp == 50
    assert b.alive is True
    b.take_damage(100)
    assert b.hp <= 0
    assert b.alive is False
