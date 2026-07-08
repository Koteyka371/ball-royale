import pytest
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.arena = type('Arena', (), {'hazards': []})
        self.boosters = []
        self.balls = []
        self.tick = 0
        self.time = 0.0

class MockBall:
    def __init__(self, id=1, hp=100, damage=10):
        self.id = id
        self.hp = hp
        self.max_hp = hp
        self.damage = damage
        self.alive = True
        self.team = "A"
        self.x = 0
        self.y = 0
        self.radius = 10
        self.ball_type = "basic"

    def take_damage(self, amount):
        self.hp -= amount

def test_reflect_booster_damage():
    attacker = MockBall(id=2, hp=100, damage=20)
    attacker.team = "B"
    attacker.x = 100

    target = MockBall(id=1, hp=100)
    target.reflect_booster_active = True
    target.reflect_booster_timer = 5.0

    world = MockWorld()
    action = Action(target, world)
    attacker.attack_accuracy = 1.0

    action._attempt_damage(attacker, target)

    assert target.hp == 100
    assert attacker.hp == 90 # 100 - (20 * 0.5)
