import pytest

class MockWorld:
    def __init__(self):
        self.events = []
        self.balls = []
        self.boosters = []
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
        for k, v in kwargs.items():
            setattr(self, k, v)

    def take_damage(self, amount):
        if not hasattr(self, "hp"):
            self.hp = 100.0
        self.hp -= amount

class MockAction:
    def __init__(self, world):
        self.world = world

def test_deflector_shield_ranged():
    world = MockWorld()
    act = MockAction(world)
    target = MockEntity(deflector_shield_active=True, hp=100.0, suspended_projectiles=[])
    attacker = MockEntity(id=2, x=100, y=100, damage=15.0)  # Ranged (distance > 30)

    from ai.action import Action
    action = Action(target, world)

    # Manually test damage attempt
    action._attempt_damage(attacker, target)

    assert len(target.suspended_projectiles) == 1
    assert target.suspended_projectiles[0]["speed"] == 600.0 * 1.5
    assert target.hp == 100.0
    assert target.deflector_shield_active == True

def test_deflector_shield_melee():
    world = MockWorld()
    act = MockAction(world)
    target = MockEntity(deflector_shield_active=True, hp=100.0, suspended_projectiles=[])
    attacker = MockEntity(id=2, x=10, y=10, damage=15.0)  # Melee (distance < 30)

    from ai.action import Action
    action = Action(target, world)

    action._attempt_damage(attacker, target)

    assert len(target.suspended_projectiles) == 0
    assert target.hp == 85.0
    assert target.deflector_shield_active == False
    assert target.stun_timer == 2.0
