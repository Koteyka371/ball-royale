import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from ai.ball_types_thief import Thief

def test_thief_initialization():
    b = Thief(1, 10.0, 20.0)
    assert b.id == 1
    assert b.hp == 65
    assert b.BALL_TYPE == "thief"
    assert b.alive is True

def test_thief_take_damage():
    b = Thief(1)
    b.take_damage(32)
    assert b.hp == 33
    assert b.alive is True
    b.take_damage(65)
    assert b.hp <= 0
    assert b.alive is False
