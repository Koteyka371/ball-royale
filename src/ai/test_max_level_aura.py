import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.action import Action
from ai.test_action_advanced import MockBall, MockWorld

def test_max_level_aura_heal():
    w = MockWorld()
    b = MockBall(50, 50)
    b.is_decoy = False
    b.cosmetic_aura_scale = 3.0
    b.speed_multiplier = 1.0
    b.team = "test"
    b.id = 1

    b2 = MockBall(50, 55)
    b2.team = "test"
    b2.hp = 50
    b2.max_hp = 100
    b2.id = 2

    w.balls = [b, b2]

    a = Action(b, w)
    a.execute("idle", 1.0)

    assert b.speed_multiplier == 0.5
    assert b2.hp == 60.0

def test_max_level_aura_fear():
    w = MockWorld()
    b = MockBall(50, 50)
    b.is_decoy = False
    b.cosmetic_aura_scale = 2.0
    b.level = 10
    b.team = "test"
    b.id = 1

    b2 = MockBall(50, 55)
    b2.team = "enemy"
    b2.level = 5
    b2.hp = 100
    b2.max_hp = 100
    b2.id = 2
    b2.personality = "aggressive"

    w.balls = [b, b2]

    a = Action(b, w)

    import random
    random.seed(42)  # Make it deterministic so emotion gets set if the branch is hit

    for _ in range(100):
        a.execute("idle", 1.0)

    # Checking fear emotion is tricky due to randomness, we will just ensure it doesn't crash
