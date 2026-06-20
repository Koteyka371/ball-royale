import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from ai.ball_types_necromancer import Necromancer

def test_necromancer_initialization():
    b = Necromancer(1, 10.0, 20.0)
    assert b.id == 1
    assert b.hp == 70
    assert b.BALL_TYPE == "necromancer"
    assert b.alive is True

def test_necromancer_take_damage():
    b = Necromancer(1)
    b.take_damage(35)
    assert b.hp == 35
    assert b.alive is True
    b.take_damage(70)
    assert b.hp <= 0
    assert b.alive is False
