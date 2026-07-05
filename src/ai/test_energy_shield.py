import pytest
from action import Action

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

def test_energy_shield_use():
    ball = MockBall()
    ball.skill = "energy_shield"
    ball.skill_timer = 0

    world = MockWorld()
    world.balls = [ball]

    action = Action(ball, world)
    action._use_skill()

    assert getattr(ball, "energy_shield_active", False) == True
    assert getattr(ball, "energy_shield_timer", 0) == 3.0

def test_energy_shield_timer():
    ball = MockBall()
    ball.energy_shield_active = True
    ball.energy_shield_timer = 3.0

    world = MockWorld()

    action = Action(ball, world)
    action._update_skill_timer(1.0)
    assert ball.energy_shield_timer == 2.0
    assert ball.energy_shield_active == True

    action._update_skill_timer(2.0)
    assert ball.energy_shield_timer <= 0
    assert ball.energy_shield_active == False

def test_energy_shield_damage_reflect_melee():
    attacker = MockBall(hp=100, damage=20)
    attacker.id = 2
    attacker.team = "B"
    attacker.x = 10 # Close range (dist=10 <= 10+10+20=40)

    target = MockBall(hp=100)
    target.energy_shield_active = True

    world = MockWorld()
    action = Action(target, world)
    attacker.attack_accuracy = 1.0

    action._attempt_damage(attacker, target)

    # target should take 0 damage
    assert target.hp == 100

    # attacker should take 50% of its damage (20 * 0.5 = 10)
    assert attacker.hp == 90

def test_energy_shield_damage_reflect_ranged():
    attacker = MockBall(hp=100, damage=20)
    attacker.id = 2
    attacker.team = "B"
    attacker.x = 100 # Long range (dist=100 > 10+10+20=40)

    target = MockBall(hp=100)
    target.energy_shield_active = True

    world = MockWorld()
    action = Action(target, world)
    attacker.attack_accuracy = 1.0

    action._attempt_damage(attacker, target)

    # target should take 0 damage
    assert target.hp == 100

    # attacker should take 150% of its damage (20 * 1.5 = 30)
    assert attacker.hp == 70
