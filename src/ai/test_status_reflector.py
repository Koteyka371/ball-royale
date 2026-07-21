import pytest
from ai.action import Action
from ai.ball_types_status_reflector import StatusReflector

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 800
        self.height = 600

    def update_zone(self, tick, delta=None):
        pass

    def clamp_position(self, x, y, radius=0):
        return x, y, False

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
        self.duration = 5.0
        self.owner_id = None
        self.active = True

class MockBall:
    def __init__(self, ball_type, hp=100.0, speed=2.0, damage=10.0, x=0.0, y=0.0, traits=None):
        self.ball_type = ball_type
        self.hp = hp
        self.speed = speed
        self.damage = damage
        self.x = x
        self.y = y
        self.id = 2
        self.team = "enemy"
        self.alive = True
        self.radius = 10.0
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.supercharge_timer = 0.0
        self.is_stunned = False
        self.stun_timer = 0.0
        self.poison_timer = 0.0
        self.blindness_timer = 0.0
        self.slow_timer = 0.0
        self.frozen_timer = 0.0
        self.burn_timer = 0.0
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

def test_status_reflector_vulnerable():
    ball = StatusReflector(1)
    # Check vulnerable
    ball.take_damage(10)
    assert ball.hp == 80 - 20 # 60
    assert ball.first_hit_taken == True

def test_status_reflector_reflects_emp():
    ball = StatusReflector(1, x=0, y=0)
    world = MockWorld()
    world.balls.append(ball)

    action = Action(ball, world)

    emp_grenade = MockHazard(kind="emp_grenade", damage=0.0, radius=50.0, x=0.0, y=0.0)
    world.arena.hazards.append(emp_grenade)

    delta = 0.1
    action.execute("idle", delta)

    # Ball should not be stunned
    assert ball.is_stunned == False
    assert getattr(ball, "stun_timer", 0.0) == 0.0

    # Hazard should be destroyed
    assert emp_grenade.duration <= 0.0 or emp_grenade.active == False

def test_status_reflector_reflects_poison():
    ball = StatusReflector(1, x=0, y=0)
    world = MockWorld()
    world.balls.append(ball)

    attacker = MockBall(ball_type="enemy", x=0, y=0)
    world.balls.append(attacker)

    action = Action(ball, world)

    poison_cloud = MockHazard(kind="poison_cloud", damage=10.0, radius=50.0, x=0.0, y=0.0)
    poison_cloud.owner_id = attacker.id
    world.arena.hazards.append(poison_cloud)

    delta = 0.1
    action.execute("idle", delta)

    # Ball should not be poisoned
    assert getattr(ball, "poison_timer", 0.0) == 0.0

    # Hazard should be destroyed
    assert poison_cloud.duration <= 0.0 or poison_cloud.active == False

    # Attacker should be poisoned
    assert attacker.poison_timer > 0.0
