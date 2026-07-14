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

    def _deal_damage(self, attacker, target):
        damage = getattr(attacker, "damage", 10.0)
        target.hp -= damage

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
    def __init__(self, kind):
        self.kind = kind
        self.x = 10.0
        self.y = 10.0
        self.active = True

def test_vampiric_aura_booster_collection():
    world = MockWorld()
    b = MockBall(id=1)
    world.balls.append(b)
    booster = MockBooster("vampiric_aura_booster")
    world.boosters.append(booster)

    action = Action(b, world)
    action._collect_booster(0.016)

    assert getattr(b, "vampiric_aura_timer", 0.0) > 0.0
    assert len(world.boosters) == 0

def test_vampiric_aura_replaces_standard_buffs():
    world = MockWorld()
    b1 = MockBall(id=1, ball_type="warrior", x=0, y=0)
    b2 = MockBall(id=2, ball_type="mage", x=10, y=10)
    b3 = MockBall(id=3, ball_type="archer", x=20, y=20)
    world.balls = [b1, b2, b3]

    b1.vampiric_aura_timer = 5.0

    action1 = Action(b1, world)
    action1._apply_friendly_aura(0.016)

    action2 = Action(b2, world)
    action2._apply_friendly_aura(0.016)

    assert getattr(b1, "has_vampiric_aura", False) == True
    assert getattr(b2, "has_vampiric_aura", False) == True

    # 3 unique classes usually mean 1.2x damage (so damage=12)
    # but vampiric aura disables standard buffs
    assert b1.damage == 12.0
    assert b2.damage == 12.0
    # Also shouldn't get speed buff (2 classes)
    assert b1.speed == 100.0
    assert b2.speed == 100.0

def test_vampiric_aura_healing():
    world = MockWorld()
    attacker = MockBall(id=1, hp=50.0) # max is 100
    target = MockBall(id=2, team="blue", hp=100.0)
    world.balls = [attacker, target]

    attacker.has_vampiric_aura = True
    attacker.damage = 20.0

    action = Action(attacker, world)
    action._attempt_damage(attacker, target)

    # Target takes 20 damage, goes from 100 to 80. (old_hp = 100, new_hp = 80)
    assert target.hp == 80.0

    # Attacker heals for 50% of 20 = 10. HP goes from 50 to 60.
    assert attacker.hp == 60.0
