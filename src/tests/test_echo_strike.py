import pytest
from ai.action import Action

class MockBall:
    def __init__(self, id, team):
        self.id = id
        self.team = team
        self.x = 0
        self.y = 0
        self.hp = 100
        self.damage = 10
        self.alive = True
        self.max_hp = 100
        self.speed = 100
        self.radius = 10
        self.attack_range = 100
        self.mass = 1
        self.ball_type = "normal"
        self.is_hologram = False

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []
    def _deal_damage(self, attacker, target, dmg=None):
        target.hp -= (dmg if dmg is not None else getattr(attacker, 'damage', 10.0))

def test_echo_attack():
    w = MockWorld()
    b1 = MockBall(1, 1)
    b2 = MockBall(2, 2)
    w.balls = [b1, b2]

    action = Action(b1, w)
    action._attempt_damage(b1, b2)
    assert b2.hp == 90.0, "Target should take 10 damage initially"

    assert hasattr(b1, 'delayed_clones') and len(b1.delayed_clones) == 1
    assert b1.delayed_clones[0]['timer'] == 1.0, "Timer should be 1.0 seconds"

    action.execute("some_strategy", 1.0)

    assert b2.hp == 86.0, "Target should take 4 follow up damage (40%)"
    assert len(b1.delayed_clones) == 0
