import pytest
import math

class MockWorld:
    def __init__(self):
        self.events = []
        self.balls = []
        self.boosters = []
        self.projectiles = []
        self.profile_manager = None
        self.tick = 0
        class MockArena:
            def __init__(self):
                self.hazards = []
        self.arena = MockArena()


class MockEntity:
    def __init__(self, **kwargs):
        self.id = 1
        self.x = 0
        self.y = 0
        self.radius = 10
        self.team = "A"
        self.ball_type = "basic"
        self.traits = []
        self.alive = True
        self.speed = 100
        for k, v in kwargs.items():
            setattr(self, k, v)

    def take_damage(self, amount):
        if not hasattr(self, "hp"):
            self.hp = 100.0
        self.hp -= amount


class MockAction:
    def __init__(self, world):
        self.world = world

def test_directional_shield_ranged_block():
    world = MockWorld()
    act = MockAction(world)
    target = MockEntity(directional_shield_active=True, directional_shield_angle=0.0, hp=100.0, suspended_projectiles=[])

    # Attacker directly to the right (angle 0)
    attacker = MockEntity(id=2, x=100, y=0, damage=15.0)  # Ranged (distance > 30)

    from ai.action import Action
    action = Action(target, world)

    action._attempt_damage(attacker, target)

    assert len(target.suspended_projectiles) == 1
    assert target.suspended_projectiles[0]["speed"] == 600.0 * 1.5
    assert target.hp == 100.0
    assert target.directional_shield_active == True

def test_directional_shield_ranged_miss():
    world = MockWorld()
    act = MockAction(world)
    target = MockEntity(directional_shield_active=True, directional_shield_angle=0.0, hp=100.0, suspended_projectiles=[])

    # Attacker behind the target (angle PI)
    attacker = MockEntity(id=2, x=-100, y=0, damage=15.0)  # Ranged (distance > 30)

    from ai.action import Action
    action = Action(target, world)

    action._attempt_damage(attacker, target)

    # Should hit because shield doesn't cover this angle
    assert len(target.suspended_projectiles) == 0
    assert target.hp == 100.0
    assert target.directional_shield_active == True

def test_directional_shield_melee_shatter():
    world = MockWorld()
    act = MockAction(world)
    target = MockEntity(directional_shield_active=True, directional_shield_angle=0.0, hp=100.0, suspended_projectiles=[])

    # Melee attack from the front (distance <= 30)
    attacker = MockEntity(id=2, x=20, y=0, damage=15.0)

    from ai.action import Action
    action = Action(target, world)

    action._attempt_damage(attacker, target)

    # Shield shatters and stuns
    assert len(target.suspended_projectiles) == 0
    assert target.hp == 85.0
    assert target.directional_shield_active == False
    assert target.stun_timer == 2.0

def test_directional_shield_use_inventory():
    world = MockWorld()
    ball = MockEntity(inventory=["deployable_directional_shield"])
    enemy = MockEntity(id=2, x=100, y=0)
    world.balls = [ball, enemy]

    from ai.action import Action
    action = Action(ball, world)
    action._get_enemies = lambda: [enemy]

    action.execute("attack", 0.1)

    assert "deployable_directional_shield" not in ball.inventory
    assert getattr(ball, "directional_shield_active", False) == True
    assert getattr(ball, "directional_shield_timer", 0) > 4.8
    assert abs(getattr(ball, "directional_shield_angle", -1) - 0.0) < 0.01
