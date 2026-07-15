import pytest
from ai.action import Action

class MockWorld:
    def __init__(self, balls):
        self.balls = balls
        self.events = []
        self.arena = None

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100
        self.alive = True
        self.skill = "swap_decoy_types"
        self.SKILL_COOLDOWN = 5.0
        self.skill_timer = 0.0
        self.ball_type = "basic"
        self.vx = 0
        self.vy = 0

def test_swap_decoy_types():
    owner = MockBall(1, 0, 0)

    decoy1 = MockBall(2, 10, 10)
    decoy1.owner_id = 1
    decoy1.is_decoy = True
    decoy1.decoy_type = "healing"

    decoy2 = MockBall(3, 20, 20)
    decoy2.owner_id = 1
    decoy2.is_decoy = True
    decoy2.decoy_type = "explosive"

    world = MockWorld([owner, decoy1, decoy2])
    world.next_id = 9999
    action = Action(owner, world)
    action._use_skill()

    assert decoy1.decoy_type != "healing"
    assert decoy1.decoy_type in ["explosive", "stun_trap", "siren"]

    assert decoy2.decoy_type != "explosive"
    assert decoy2.decoy_type in ["healing", "stun_trap", "siren"]

    assert owner.skill_timer > 0
