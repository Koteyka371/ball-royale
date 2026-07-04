import pytest
from action import Action

class MockWorld:
    def __init__(self):
        self.balls = []

    def get_nearby_entities(self, target, radius):
        allies = [b for b in self.balls if b != target and getattr(b, "team", "A") == getattr(target, "team", "A")]
        return {"allies": allies, "enemies": []}

class MockBall:
    def __init__(self, hp=100, damage=10, b_type="normal", team="A"):
        self.hp = hp
        self.max_hp = hp
        self.damage = damage
        self.alive = True
        self.id = 1
        self.team = team
        self.ball_type = b_type
        self.x = 0
        self.y = 0

    def take_damage(self, amount):
        self.hp -= amount

def test_shield_drone_intercepts_damage():
    attacker = MockBall(hp=100, damage=20, team="B")
    attacker.attack_accuracy = 1.0

    target = MockBall(hp=100, team="A")
    shield_drone = MockBall(hp=150, b_type="shield_drone", team="A")
    shield_drone.id = 2

    world = MockWorld()
    world.balls = [attacker, target, shield_drone]

    action = Action(target, world)
    action._attempt_damage(attacker, target)

    assert target.hp == 100
    assert shield_drone.hp == 130
