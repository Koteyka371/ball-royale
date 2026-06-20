import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from ai.ball_types_pirate import Pirate

def test_pirate_initialization():
    b = Pirate(1, 10.0, 20.0)
    assert b.id == 1
    assert b.hp == 105
    assert b.BALL_TYPE == "pirate"
    assert b.alive is True

def test_pirate_take_damage():
    b = Pirate(1)
    b.take_damage(52)
    assert b.hp == 53
    assert b.alive is True
    b.take_damage(105)
    assert b.hp <= 0
    assert b.alive is False
