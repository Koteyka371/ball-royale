import math
from ai.action import Action

class MockWorld:
    pass

class MockBall:
    def __init__(self, hp=100, damage=10):
        self.hp = hp
        self.max_hp = hp
        self.damage = damage
        self.alive = True
        self.id = 1
        self.team = "A"
        self.x = 0
        self.y = 0
        self.radius = 10

    def take_damage(self, amount):
        self.hp -= amount

def test_surge_shield_use():
    ball = MockBall()
    ball.skill = "surge_shield"
    ball.skill_timer = 0

    world = MockWorld()
    world.balls = [ball]

    action = Action(ball, world)
    action._use_skill()

    assert getattr(ball, "surge_shield_active", False) == True
    assert getattr(ball, "surge_shield_timer", 0) == 3.0

def test_surge_shield_timer():
    ball = MockBall()
    ball.surge_shield_active = True
    ball.surge_shield_timer = 3.0

    world = MockWorld()

    action = Action(ball, world)
    action._update_skill_timer(1.0)
    assert ball.surge_shield_timer == 2.0
    assert ball.surge_shield_active == True

    action._update_skill_timer(2.0)
    assert ball.surge_shield_timer <= 0
    assert ball.surge_shield_active == False

def test_surge_shield_damage_absorb():
    attacker = MockBall(hp=100, damage=20)
    attacker.id = 2
    attacker.team = "B"
    attacker.x = 10

    target = MockBall(hp=100)
    target.surge_shield_active = True
    target.stamina = 50.0
    target.max_stamina = 100.0

    world = MockWorld()
    action = Action(target, world)
    attacker.attack_accuracy = 1.0

    action._attempt_damage(attacker, target)

    # target should take 0 damage
    assert target.hp == 100

    # speed should be boosted
    assert getattr(target, "speed_boost_timer", 0.0) == 3.0

    # stamina should be increased by 20 (damage * 1.0)
    assert target.stamina == 70.0

    # max stamina should be increased by 20
    assert target.max_stamina == 120.0
