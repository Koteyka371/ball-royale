import pytest
from unittest.mock import Mock
from ai.action import Action

class MockBall:
    def __init__(self, **kwargs):
        self.id = 1
        self.team = "A"
        self.x = 0
        self.y = 0
        self.stamina = 50.0
        self.max_stamina = 100.0
        self.hp = 100.0
        self.alive = True
        self.is_dashing = False
        self.stutter_timer = 0.0
        for k, v in kwargs.items():
            setattr(self, k, v)

class MockWorld:
    def __init__(self, balls):
        self.balls = balls

def test_vampiric_aura_stamina_drain():
    b1 = MockBall(id=1, vampiric_aura_timer=10.0, stamina=50.0)
    b2 = MockBall(id=2, team="B", x=50, y=0, stamina=100.0)

    world = MockWorld([b1, b2])

    a1 = Action(b1, world)
    a1.execute('idle', 1.0)

    assert b1.stamina > 50.0
    assert b2.stamina < 100.0
