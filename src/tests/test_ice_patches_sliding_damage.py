import pytest

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.game_mode = None
        def get_nearby_entities(target, radius):
            return {"allies": [], "enemies": []}
        self.get_nearby_entities = get_nearby_entities
        def _deal_damage(attacker, target):
            target.take_damage(attacker.damage)
        self._deal_damage = _deal_damage

class MockHazard:
    def __init__(self, kind, x, y, radius):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.active = True

class MockBall:
    def __init__(self, x=0, y=0, radius=10):
        self.id = id(self)
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = radius
        self.damage = 10.0
        self.team = 1
        self.hp = 100.0
        self.max_hp = 100.0
        self.ball_type = "normal"
        self.alive = True
        self.intangible = False
        self.ghost_mode_active = False
        self.is_projectile = False
        self.is_spell = False
        self.is_energy = False

    def take_damage(self, amount):
        self.hp -= amount

def test_ice_patches_sliding_damage_normal():
    from ai.action import Action
    world = MockWorld()

    attacker = MockBall(0, 0)
    attacker.team = 1
    attacker.vx = 0.0
    attacker.vy = 0.0

    target = MockBall(30, 0)
    target.team = 2

    action = Action(attacker, world)
    action._attempt_damage(attacker, target)

    assert target.hp == 90.0, f"Expected 90.0, got {target.hp}"

def test_ice_patches_sliding_damage_sliding():
    import math
    from ai.action import Action
    world = MockWorld()

    attacker = MockBall(0, 0)
    attacker.team = 1
    attacker.vx = 200.0
    attacker.vy = 0.0

    target = MockBall(30, 0)
    target.team = 2

    ice_patch = MockHazard("ice_patches", 0, 0, 30.0)
    world.arena.hazards.append(ice_patch)

    action = Action(attacker, world)
    action._attempt_damage(attacker, target)

    # Base 10.0 damage.
    # Attacker sliding on ice patches, vx=200, vel=200
    # Multiplier: 1.0 + (200 / 200.0) = 2.0. So 20.0 damage.
    # HP: 100 - 20.0 = 80.0
    assert target.hp == 80.0, f"Expected 80.0, got {target.hp}"

def test_ice_patches_sliding_damage_high_speed():
    from ai.action import Action
    world = MockWorld()

    attacker = MockBall(0, 0)
    attacker.team = 1
    attacker.vx = 800.0
    attacker.vy = 0.0

    target = MockBall(30, 0)
    target.team = 2

    ice_patch = MockHazard("ice_patches", 0, 0, 30.0)
    world.arena.hazards.append(ice_patch)

    action = Action(attacker, world)
    action._attempt_damage(attacker, target)

    # 800 vel -> 1.0 + 800/200 = 5.0, but clamped to 3.0
    # 10.0 * 3.0 = 30.0
    # HP: 100 - 30.0 = 70.0
    assert target.hp == 70.0, f"Expected 70.0, got {target.hp}"
