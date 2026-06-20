import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from ai.ball_types_cyborg import Cyborg

def test_cyborg_initialization():
    b = Cyborg(1, 10.0, 20.0)
    assert b.id == 1
    assert b.hp == 140
    assert b.BALL_TYPE == "cyborg"
    assert b.alive is True

def test_cyborg_take_damage():
    b = Cyborg(1)
    b.take_damage(70)
    assert b.hp == 70
    assert b.alive is True
    b.take_damage(140)
    assert b.hp <= 0
    assert b.alive is False
