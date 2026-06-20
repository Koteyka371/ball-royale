import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from ai.ball_types_shaman import Shaman

def test_shaman_initialization():
    b = Shaman(1, 10.0, 20.0)
    assert b.id == 1
    assert b.hp == 90
    assert b.BALL_TYPE == "shaman"
    assert b.alive is True

def test_shaman_take_damage():
    b = Shaman(1)
    b.take_damage(45)
    assert b.hp == 45
    assert b.alive is True
    b.take_damage(90)
    assert b.hp <= 0
    assert b.alive is False
