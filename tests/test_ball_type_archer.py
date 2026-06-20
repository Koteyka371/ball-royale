import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from ai.ball_types_archer import Archer

def test_archer_initialization():
    b = Archer(1, 10.0, 20.0)
    assert b.id == 1
    assert b.hp == 75
    assert b.BALL_TYPE == "archer"
    assert b.alive is True

def test_archer_take_damage():
    b = Archer(1)
    b.take_damage(37)
    assert b.hp == 38
    assert b.alive is True
    b.take_damage(75)
    assert b.hp <= 0
    assert b.alive is False
