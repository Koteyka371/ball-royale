import pytest
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.balls = []
        self.next_id = 1000
        self.arena = MockArena()
        self.events = []

class MockArena:
    def __init__(self):
        self.hazards = []

class MockBall:
    def __init__(self, id, x, y, hp=100):
        self.id = id
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp
        self.alive = True
        self.is_decoy = False
        self.skill = "deploy_decoy_black_hole"
        self.SKILL_COOLDOWN = 10.0
        self.skill_timer = 0.0
        self.active_skill = "deploy_decoy_black_hole"
        self.team = "team1"
        self.vx = 0
        self.vy = 0

def test_deploy_decoy_black_hole():
    world = MockWorld()
    ball = MockBall(1, 100, 100)
    world.balls.append(ball)

    action = Action(ball, world)
    action._use_skill()

    assert ball.skill_timer > 0

    decoys = [b for b in world.balls if getattr(b, "is_decoy", False)]
    assert len(decoys) >= 1
    assert any(d.decoy_type == "black_hole" for d in decoys)
