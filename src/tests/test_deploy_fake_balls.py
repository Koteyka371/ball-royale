import pytest
import math
from ai.action import Action

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.max_hp = 100
        self.hp = 100
        self.skill = "deploy_fake_balls"
        self.skill_timer = 0.0
        self.invisibility_timer = 0.0
        self.inventory = []
        self.use_item = False
        self.experience = 0.0
        self.damage = 10
        self.vx = 0
        self.vy = 0
        self.brain = "some_brain"
        self.active_skill = "deploy_fake_balls"
        self.SKILL = "deploy_fake_balls"

class MockWorld:
    def __init__(self):
        self.balls = []
        self.next_id = 1000

def test_deploy_fake_balls():
    world = MockWorld()
    ball = MockBall(1, 0, 0)
    world.balls.append(ball)

    action = Action(ball, world)
    action._use_skill()

    assert ball.invisibility_timer == 2.0

    assert len(world.balls) == 4

    fake_balls = [b for b in world.balls if b != ball]
    for b in fake_balls:
        assert getattr(b, "is_decoy_clone", False)
        assert getattr(b, "is_illusion", False)
        assert getattr(b, "hp", 0) == 50
        assert b.damage == 0
        assert getattr(b, "invisibility_timer", -1) == 0.0
        assert b.skill is None
        assert b.SKILL is None
        assert getattr(b, "active_skill", None) is None
        assert getattr(b, "brain", None) is None
