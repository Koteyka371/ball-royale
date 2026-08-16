import pytest
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
        self.is_night = False
        self.is_lunar_eclipse = False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []
        self.events = []

    def get_nearby_entities(self, ball, radius):
        return {"allies": [], "boosters": self.boosters}

class MockBall:
    def __init__(self, id, team="red", ball_type="warrior", x=0.0, y=0.0, hp=100.0, max_hp=100.0):
        self.id = id
        self.team = team
        self.ball_type = ball_type
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp
        self.alive = True
        self.speed = 100.0
        self.base_speed = 100.0
        self.damage = 10.0
        self.base_damage = 10.0

class MockBooster:
    def __init__(self, kind, x=0.0, y=0.0):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = 15.0

def test_permanent_aura_booster():
    world = MockWorld()
    b1 = MockBall(1, team="red")
    b2 = MockBall(2, team="red", x=50, y=50) # Ally

    world.balls = [b1, b2]

    # Spawn the new booster
    booster = MockBooster("permanent_aura_booster", 10.0, 10.0)
    world.boosters.append(booster)

    action1 = Action(b1, world)

    # Run _collect_booster
    action1._collect_booster(0.016)

    # Verify pickup
    assert len(world.boosters) == 0
    assert hasattr(world, "permanent_aura_buffs")
    assert world.permanent_aura_buffs.get("red", 0) == 1

    # Test `_apply_friendly_aura` indirectly or by checking the logic directly
    # A single stack gives +100 radius and +0.5 multiplier.
    # Base radius is 150.0, multiplier is 1.0. With 1 stack it should be 250.0 and 1.5.

    # Let's add an enemy to check if radius increased properly, or we can just mock/verify properties.
    # We will verify by looking at the HP regen for a 1-stack ally (which usually gives 2.0 * aura_multiplier regen).
    # Normally regen = 2.0 * multiplier * delta = 2.0 * 1.5 * delta = 3.0 * delta.
    b1.hp = 50.0
    action1._apply_friendly_aura(0.1) # 2 type, gives HP regen
    # Wait, they are both "warrior", so unique types = 1 (no extra types).
    # Let's make b2 a different type to get stack_count = 1.
    b2.ball_type = "paladin"
    action1._apply_friendly_aura(0.1)

    # With 1 extra type (stack_count=1), base regen is 2.0 * aura_multiplier * delta.
    # aura_multiplier should be 1.0 + 0.5 = 1.5
    # Regen = 2.0 * 1.5 * 0.1 = 0.3
    # b1.hp should be 50.0 + 0.3 = 50.3
    assert abs(b1.hp - 50.3) < 0.001

def test_permanent_aura_booster_multiple_stacks():
    world = MockWorld()
    b1 = MockBall(1, team="blue")
    b2 = MockBall(2, team="blue", x=50, y=50, ball_type="mage") # Ally
    world.balls = [b1, b2]

    world.permanent_aura_buffs = {"blue": 3}

    action1 = Action(b1, world)

    b1.hp = 50.0
    action1._apply_friendly_aura(0.1)

    # With 3 stacks, aura_multiplier = 1.0 + 1.5 = 2.5
    # Regen = 2.0 * 2.5 * 0.1 = 0.5
    assert abs(b1.hp - 50.5) < 0.001
