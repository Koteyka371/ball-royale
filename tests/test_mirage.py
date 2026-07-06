import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from ai.action import Action
from ai.ball_types_mirage import Mirage

class MockArena:
    hazards = []

class MockWorld:
    def __init__(self):
        self.balls = []
        self.next_id = 1000
        self.arena = MockArena()
        self.width = 1000
        self.height = 1000

class MockBall:
    def __init__(self, id, x=0, y=0, max_hp=100, damage=10):
        self.id = id
        self.x = x
        self.y = y
        self.max_hp = max_hp
        self.hp = max_hp
        self.damage = damage
        self.alive = True
        self.is_decoy = False
        self.is_illusion = False
        self.is_active_clone = False

def test_global_mirage_skill():
    world = MockWorld()

    mirage_ball = Mirage(ball_id=1, x=10, y=10)
    mirage_ball.skill = "global_mirage"
    mirage_ball.SKILL = "global_mirage"

    b2 = MockBall(id=2, x=20, y=20)
    b3 = MockBall(id=3, x=30, y=30)

    world.balls = [mirage_ball, b2, b3]

    action = Action(mirage_ball, world)
    action.ball.active_skill = "global_mirage"

    action._spawn_skill_particles = lambda x: None
    action.ball.skill_timer = 0

    action.execute("use_skill", 1.0)

    # 3 original balls + 3 decoys = 6
    assert len(world.balls) == 6

    decoys = world.balls[3:]
    assert len(decoys) == 3

    for d in decoys:
        assert d.is_active_clone == True
        assert d.is_illusion == True
        assert d.hp in (50.0, 40.0)
        assert d.damage == 5.0 # 10 * 0.5
        assert d.mimic_timer == 15.0
        assert d.skill is None
        assert d.skill_timer == 9999.0
