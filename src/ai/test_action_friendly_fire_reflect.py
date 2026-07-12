import sys
sys.path.append("src")
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.events = []

    def _deal_damage(self, attacker, target):
        target.take_damage(attacker.damage)

    def get_nearby_entities(self, target, radius):
        return {"allies": []}

class MockBall:
    def __init__(self, id, hp=100, damage=10, team="A"):
        self.id = id
        self.hp = hp
        self.max_hp = hp
        self.damage = damage
        self.team = team
        self.x = 0
        self.y = 0
        self.radius = 10
        self.alive = True
        self.ball_type = "normal"
        self.attack_accuracy = 1.0
        self.friendly_fire_reflect_timer = 5.0

    def take_damage(self, amount):
        self.hp -= amount

def test_friendly_fire():
    attacker = MockBall(1, hp=100, damage=10, team="A")
    target = MockBall(2, hp=100, damage=10, team="A")

    world = MockWorld()
    world.balls = [attacker, target]

    action = Action(target, world)
    action._attempt_damage(attacker, target)

    print(f"Target HP: {target.hp}")
    print(f"Attacker HP: {attacker.hp}")

test_friendly_fire()
