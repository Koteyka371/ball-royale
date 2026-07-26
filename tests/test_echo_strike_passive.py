import pytest
from src.ai.action import Action

class MockWorld:
    def __init__(self):
        self.balls = []
        self._deal_damage_calls = []

    def _deal_damage(self, attacker, target, dmg=None):
        if dmg is not None:
            self._deal_damage_calls.append((attacker, target, dmg))
        else:
            self._deal_damage_calls.append((attacker, target, getattr(attacker, 'damage', 10.0)))

class MockBall:
    def __init__(self, **kwargs):
        self.id = 1
        self.x = 0
        self.y = 0
        self.team = 1
        self.alive = True
        self.damage = 10.0
        self.attack_timer = 0.0
        self.echo_strike_count = 0
        self.speed = 1.0
        for k, v in kwargs.items():
            setattr(self, k, v)

    def has_passive(self, p):
        return p == getattr(self, 'passive', '')

def test_echo_strike_passive_triggers():
    world = MockWorld()

    ball = MockBall(id=1, x=0, y=0, team=1, passive="echo_strike")
    target = MockBall(id=2, x=10, y=10, team=2)
    nearby_enemy = MockBall(id=3, x=15, y=15, team=2)
    far_enemy = MockBall(id=4, x=100, y=100, team=2)

    world.balls = [ball, target, nearby_enemy, far_enemy]

    action = Action(ball, world)

    ball.attack_timer = 0.0
    action._get_enemies = lambda: [target, nearby_enemy, far_enemy]

    for i in range(3):
        ball.attack_timer = 0.0
        action._attack(delta=1.0)

    assert ball.echo_strike_count == 0

    echo_calls = [c for c in world._deal_damage_calls if getattr(c[0], 'damage', 0) == 5.0 and c[1].id == 3]
    assert len(echo_calls) >= 1
