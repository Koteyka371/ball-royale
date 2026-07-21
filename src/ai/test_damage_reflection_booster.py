import sys
sys.path.append("src")
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.events = []

class MockBall:
    def __init__(self, id, hp=100, damage=10):
        self.id = id
        self.hp = hp
        self.max_hp = hp
        self.damage = damage
        self.team = "A"
        self.x = 0
        self.y = 0
        self.radius = 10
        self.alive = True
        self.ball_type = "normal"
        self.damage_reflection_active = True
        self.damage_reflection_timer = 5.0

    def take_damage(self, amount):
        self.hp -= amount

def test_damage_reflection():
    attacker = MockBall(1, hp=100, damage=20)
    target = MockBall(2, hp=100, damage=10)
    target.team = "B"

    world = MockWorld()
    world.balls = [attacker, target]

    action = Action(target, world)
    action._attempt_damage(attacker, target)

    assert target.hp == 100.0, f"Expected target to take 0 dmg, got {100 - target.hp}"
    assert attacker.hp == 90.0, f"Expected attacker to take 10 dmg, got {100 - attacker.hp}"

if __name__ == "__main__":
    test_damage_reflection()
