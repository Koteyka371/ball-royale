import math
import sys
import pytest

# Adding src to path so ai imports work
sys.path.append("src")
from ai.action import Action

class DummyWorld:
    def __init__(self):
        self.arena = DummyArena()
        self.profile_manager = None
    def _deal_damage(self, attacker, target, dmg=None):
        target.hp -= (dmg if dmg else attacker.damage)

class DummyArena:
    def __init__(self):
        self.hazards = []

class DummyHazard:
    def __init__(self, x, y, r, kind):
        self.x = x
        self.y = y
        self.radius = r
        self.kind = kind

class DummyBall:
    def __init__(self):
        self.x = -100
        self.y = 0
        self.radius = 10
        self.hp = 100
        self.alive = True
        self.damage = 10
        self.ball_type = "sniper"
        self.base_speed = 100.0
        self.speed = 100.0
        self.speed_multiplier = 1.0
        self.skill_timer = 5.0
        self.max_stamina = 100.0
        self.stamina = 10.0

def test_slow_motion_zone_speed_cooldown():
    world = DummyWorld()
    ball = DummyBall()
    ball.x = 0
    ball.y = 0

    action = Action(1, world)
    action.ball = ball

    world.arena.hazards.append(DummyHazard(0, 0, 50.0, "slow_motion_zone"))

    action.execute("idle", 1.0)

    # speed and multiplier should be halved
    assert ball.slow_motion_zone_active == True
    assert ball.speed == 50.0
    assert ball.speed_multiplier == 0.5

    # skill_timer was 5.0, normally decreases by 1.0, but with zone decreases by 0.5
    # Wait, 5.0 - 0.5 = 4.5
    assert math.isclose(ball.skill_timer, 4.5)

    # 10.0 + 60.0 * 1.0 = 70.0
    assert math.isclose(ball.stamina, 70.0)

def test_slow_motion_zone_projectile_suspension():
    world = DummyWorld()
    attacker = DummyBall()
    attacker.x = -100
    attacker.y = 0

    target = DummyBall()
    target.x = 100
    target.y = 0

    action = Action(1, world)
    action.ball = attacker

    world.arena.hazards.append(DummyHazard(0, 0, 50.0, "slow_motion_zone"))

    action._attempt_damage(attacker, target)

    # Attack should be blocked and suspended
    assert len(getattr(attacker, "suspended_projectiles", [])) == 1
    assert target.hp == 100

    # Simulate time passing (1.0 sec)
    action.execute("idle", 1.0)
    assert len(attacker.suspended_projectiles) == 1
    assert target.hp == 100

    # Simulate more time passing (1.1 sec, total 2.1)
    action.execute("idle", 1.1)

    # Projectile should resume and hit
    assert len(attacker.suspended_projectiles) == 0
    assert target.hp <= 90 # Damage taken

def test_slow_motion_trap_speed():
    world = DummyWorld()
    ball = DummyBall()
    ball.x = 0
    ball.y = 0

    action = Action(1, world)
    action.ball = ball

    world.arena.hazards.append(DummyHazard(0, 0, 50.0, "slow_motion_trap"))

    action.execute("idle", 1.0)

    # speed and multiplier should be 0.2
    assert getattr(ball, "slow_motion_zone_active", False) == True
    assert getattr(ball, "speed", 0.0) == 20.0
    assert getattr(ball, "speed_multiplier", 1.0) == 0.2

    # skill_timer was 5.0, normally decreases by 1.0, but with zone decreases by 0.5 (since slow_motion_zone_active is True, it gets 0.5 mult)
    import math
    assert math.isclose(ball.skill_timer, 4.5)
