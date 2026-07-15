import pytest
from ai.action import Action

class MockBall:
    def __init__(self, x=0, y=0, team="red"):
        self.id = id(self)
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.hp = 100
        self.stutter_timer = 0
        self.silence_timer = 0
        self.decoy_timer = 0

class MockWorld:
    def __init__(self, balls):
        self.balls = balls
        self.events = []

def test_emp_combo():
    # Owner
    owner = MockBall(0, 0, "red")

    # Decoy 1 (explosive)
    d1 = MockBall(10, 10, "red")
    d1.is_decoy = True
    d1.hp = 0
    d1.owner_id = owner.id
    d1.decoy_type = "explosive"

    # Decoy 2 (stun)
    d2 = MockBall(15, 15, "red")
    d2.is_decoy = True
    d2.hp = 0
    d2.owner_id = owner.id
    d2.decoy_type = "stun_trap"

    # Enemy
    enemy = MockBall(12, 12, "blue")

    world = MockWorld([owner, d1, d2, enemy])

    action = Action(d1, world)
    action.execute({}, 0.1)

    assert getattr(d1, "_decoy_exploded", False) is True
    assert getattr(d2, "_decoy_exploded", False) is True

    assert enemy.silence_timer > 0
