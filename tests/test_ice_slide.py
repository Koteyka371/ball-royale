import pytest
from src.ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []

class MockHazard:
    def __init__(self, kind, x, y, radius):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.active = True
        self.is_disabled_by_flare = False

class MockBall:
    def __init__(self, name, x, y, hp, damage):
        self.name = name
        self.x = x
        self.y = y
        self.hp = hp
        self.damage = damage
        self.vx = 0.0
        self.vy = 0.0
        self.team = name
        self.radius = 10.0

def test_ice_slide_multiplier():
    world = MockWorld()
    ice_patch = MockHazard("ice_patches", 100.0, 100.0, 50.0)
    world.arena.hazards.append(ice_patch)

    attacker = MockBall("attacker", 100.0, 100.0, 100.0, 10.0)
    attacker.vx = 200.0
    attacker.vy = 0.0

    target = MockBall("target", 200.0, 200.0, 100.0, 10.0)

    action = Action(attacker, world)

    # Target not on ice patch, so damage_reduction = 1.0
    # Mock the random check
    import random
    import sys
    sys.modules['random'] = __import__('unittest.mock').mock.Mock()
    sys.modules['random'].random = lambda: 0.0

    print(f"Before attempt damage: target HP = {target.hp}")

    # We need a MockWorld with a _deal_damage function
    def mock_deal_damage(attacker, target):
        # We need to capture the temporarily set 'damage' property
        damage = getattr(attacker, "damage", 10.0)
        target.hp -= damage

    world._deal_damage = mock_deal_damage

    action._attempt_damage(attacker, target)
    print(f"After attempt damage: target HP = {target.hp}")

    # speed = 200.0, so multiplier should be 1.0 + 200.0 / 100.0 = 3.0
    # original damage = 10.0 * 3.0 = 30.0
    # target HP should be 100.0 - 30.0 = 70.0
    print(f"Target HP: {target.hp}")
    assert abs(target.hp - 70.0) < 0.01
