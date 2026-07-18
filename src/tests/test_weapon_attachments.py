import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.action import Action

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.boosters = []
        self.balls = []

    def _deal_damage(self, attacker, target):
        target.take_damage(attacker.damage)

class MockBall:
    def __init__(self, id, x, y, team):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.radius = 10.0
        self.hp = 100.0
        self.damage = 10.0
        self.alive = True
        self.is_projectile = False
        self.is_energy = False
        self.intangible = False

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

def test_fire_attachment():
    world = MockWorld()
    b1 = MockBall(1, 100, 100, 1)
    b1.fire_attachment_timer = 15.0
    b2 = MockBall(2, 120, 100, 2)
    world.balls = [b1, b2]

    action = Action(b1, world)
    action._attempt_damage(b1, b2)

    assert getattr(b2, "dot_duration", 0.0) == 2.0
    assert getattr(b2, "dot_damage_per_tick", 0.0) == 2.0

def test_ice_attachment():
    world = MockWorld()
    b1 = MockBall(1, 100, 100, 1)
    b1.ice_attachment_timer = 15.0
    b2 = MockBall(2, 120, 100, 2)
    world.balls = [b1, b2]

    action = Action(b1, world)
    action._attempt_damage(b1, b2)

    assert getattr(b2, "slow_timer", 0.0) == 2.0

def test_spread_attachment():
    world = MockWorld()
    b1 = MockBall(1, 100, 100, 1)
    b1.spread_attachment_timer = 15.0
    b2 = MockBall(2, 120, 100, 2) # Target
    b3 = MockBall(3, 130, 100, 2) # Near target (dist 10)
    b4 = MockBall(4, 300, 300, 2) # Far from target
    world.balls = [b1, b2, b3, b4]

    action = Action(b1, world)
    action._attempt_damage(b1, b2)

    # b3 should take 50% damage
    assert b3.hp == 95.0
    # b4 shouldn't take damage
    assert b4.hp == 100.0

def test_pierce_attachment():
    world = MockWorld()
    b1 = MockBall(1, 100, 100, 1)
    b1.pierce_attachment_timer = 15.0
    b2 = MockBall(2, 120, 100, 2) # Target
    b3 = MockBall(3, 140, 100, 2) # Behind target (x axis aligns perfectly)
    b4 = MockBall(4, 100, 120, 2) # Beside attacker
    world.balls = [b1, b2, b3, b4]

    action = Action(b1, world)
    action._attempt_damage(b1, b2)

    # b3 should take 50% damage
    assert b3.hp == 95.0
    # b4 shouldn't take damage
    assert b4.hp == 100.0

def test_timer_decrement():
    world = MockWorld()
    b1 = MockBall(1, 100, 100, 1)
    b1.fire_attachment_timer = 15.0
    b1.ice_attachment_timer = 15.0
    b1.spread_attachment_timer = 15.0
    b1.pierce_attachment_timer = 15.0
    action = Action(b1, world)

    action.execute("idle", 1.0)

    assert b1.fire_attachment_timer == 14.0
    assert b1.ice_attachment_timer == 14.0
    assert b1.spread_attachment_timer == 14.0
    assert b1.pierce_attachment_timer == 14.0
import pytest

def test_laser_sight_attachment():
    from ai.action import Action

    class MockEntity:
        def __init__(self, kind, x=0, y=0):
            self.kind = kind
            self.x = x
            self.y = y

    class MockArena:
        def __init__(self, hazards):
            self.hazards = hazards
            self.is_foggy = False
            self.width = 1000.0
            self.height = 1000.0
            self.safe_zone_center = (500.0, 500.0)
            self.safe_zone_radius = 500.0
        def get(self, key, default=None):
            return getattr(self, key, default)

    class MockWorld:
        def __init__(self, arena, boosters):
            self.arena = arena
            self.boosters = boosters
            self.balls = []
            self.current_mode_name = "default"
        def _deal_damage(self, attacker, target):
            pass

    class MockBall:
        def __init__(self):
            self.x = 0
            self.y = 0
            self.radius = 10
            self.attack_range = 150.0
            self.id = 1
            self.team = "blue"
            self.ball_type = "default"
            self.alive = True
            self.speed = 2.0
            self.traits = []

    laser_sight = MockEntity("laser_sight_attachment")
    arena = MockArena([laser_sight])
    world = MockWorld(arena, [laser_sight])
    ball = MockBall()

    action = Action(ball, world)

    action._get_enemies_internal = lambda: []
    action._get_boosters = lambda: [laser_sight]
    action._collect_booster(1.0)

    assert getattr(ball, "laser_sight_timer", 0.0) == 15.0
    assert getattr(ball, "laser_sight_applied", False) is True
    assert getattr(ball, "base_attack_range", 150.0) == 150.0
    assert getattr(ball, "attack_range", 150.0) == 225.0
    assert laser_sight not in world.boosters

    ball.skill_timer = 5.0
    enemy = MockBall()
    enemy.id = 2
    enemy.team = "red"
    enemy.in_mirror_dimension = False
    ball.in_mirror_dimension = False

    action._attempt_damage(ball, enemy)

    assert getattr(ball, "skill_timer", 5.0) == 4.5

    action.execute("flee", 16.0)

    assert getattr(ball, "laser_sight_timer", 0.0) <= 0.0
    assert getattr(ball, "laser_sight_applied", True) is False
    assert getattr(ball, "attack_range", 0.0) == 150.0
