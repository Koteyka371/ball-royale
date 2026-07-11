import pytest
from ai.action import Action
import math

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 800
        self.height = 600

    def update_zone(self, tick, delta=None):
        pass

    def clamp_position(self, x, y, radius=0):
        return x, y, False

class MockBall:
    def __init__(self, ball_type, hp=100.0, speed=2.0, damage=10.0, x=0.0, y=0.0, traits=None):
        self.ball_type = ball_type
        self.hp = hp
        self.speed = speed
        self.damage = damage
        self.x = x
        self.y = y
        self.id = 1
        self.team = "test_team"
        self.alive = True
        self.radius = 10.0
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.supercharge_timer = 0.0
        self.stutter_timer = 0.0
        self.is_stunned = False
        self.stun_timer = 0.0
        self.speed_buff_timer = 0.0
        self.damage_buff_timer = 0.0
        self.emp_immunity_timer = 0.0
        self.damage_booster_timer = 0.0
        self.base_speed = speed
        self.base_damage = damage
        self.traits = traits if traits is not None else []

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []

class MockHazard:
    def __init__(self, kind, damage, radius, x, y, hit_targets=False):
        self.id = 1
        self.kind = kind
        self.damage = damage
        self.radius = radius
        self.x = x
        self.y = y
        self.hit_targets = hit_targets

def test_emp_grenade_robotic_drone():
    ball = MockBall(ball_type="drone")
    world = MockWorld()
    world.balls.append(ball)

    action = Action(ball, world)
    ball.supercharge_timer = 5.0
    ball.speed_buff_timer = 5.0

    emp_grenade = MockHazard(kind="emp_grenade", damage=0.0, radius=50.0, x=0.0, y=0.0)
    world.arena.hazards.append(emp_grenade)

    delta = 0.1
    action.execute("idle", delta)

    assert ball.is_stunned == True
    assert ball.stun_timer == 2.9

    # Buffs should be cleared
    assert ball.supercharge_timer == 0.0
    assert ball.speed_buff_timer == 0.0

def test_emp_grenade_metal_trait():
    ball = MockBall(ball_type="warrior", traits=["metal"])
    world = MockWorld()
    world.balls.append(ball)

    action = Action(ball, world)
    ball.supercharge_timer = 5.0
    ball.damage_buff_timer = 5.0

    emp_grenade = MockHazard(kind="emp_grenade", damage=0.0, radius=50.0, x=0.0, y=0.0)
    world.arena.hazards.append(emp_grenade)

    delta = 0.1
    action.execute("idle", delta)

    assert ball.is_stunned == True
    assert ball.stun_timer == 2.9

    # Buffs should be cleared
    assert ball.supercharge_timer == 0.0
    assert ball.damage_buff_timer == 0.0

def test_emp_grenade_non_robotic():
    ball = MockBall(ball_type="mage")
    world = MockWorld()
    world.balls.append(ball)

    action = Action(ball, world)
    ball.supercharge_timer = 5.0
    ball.speed_buff_timer = 5.0

    emp_grenade = MockHazard(kind="emp_grenade", damage=0.0, radius=50.0, x=0.0, y=0.0)
    world.arena.hazards.append(emp_grenade)

    delta = 0.1
    action.execute("idle", delta)

    assert ball.is_stunned == False
    assert ball.stun_timer == 0.0

    # Buffs should be cleared even for non-robotic balls
    assert ball.supercharge_timer == 0.0
    assert ball.speed_buff_timer == 0.0
