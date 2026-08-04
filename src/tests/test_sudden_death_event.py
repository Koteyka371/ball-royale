import pytest
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ai.game_modes import SuddenDeathEventMode

class MockWorld:
    def __init__(self):
        self.arena = None
        self.dead_balls = []
        self.world_state = "playing"

class MockBall:
    def __init__(self, id, hp, skill_cooldown):
        self.id = id
        self.hp = hp
        self.skill_cooldown = skill_cooldown

def test_sudden_death_event():
    mode = SuddenDeathEventMode()
    b1 = MockBall("b1", 100.0, 10.0)
    balls = [b1]
    world = MockWorld()

    mode.setup(world, balls)
    mode.tick(world, balls, 0.016)

    # Cooldown should be reduced by 50%
    assert b1.skill_cooldown == 5.0

    # Take damage manually
    b1.hp -= 20.0

    mode.tick(world, balls, 0.016)

    # Damage taken should be doubled: took 20, should subtract 20 more, so -40 total
    assert b1.hp == 60.0

    # Cooldown should not be reduced again
    assert b1.skill_cooldown == 5.0
