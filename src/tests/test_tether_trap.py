import pytest
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []

    def _deal_damage(self, owner, target):
        target.hp -= getattr(owner, "damage", 10.0)

class MockArena:
    def __init__(self):
        self.hazards = []

class MockHazard:
    def __init__(self, id, x, y, kind, radius=60.0, damage=10.0, owner_id=1):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = radius
        self.damage = damage
        self.owner_id = owner_id
        self.duration = 10.0

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.hp = 100.0
        self.alive = True
        self.inventory = []
        self.damage = 10.0
        self.speed = 2.0
        self.perception_radius = 50.0

def test_tether_trap():
    world = MockWorld()
    # Trap at 0, 0
    # Ball 1 at 30, 0 (inside radius 60)
    ball1 = MockBall(2, 30.0, 0.0)
    world.balls = [ball1]

    trap = MockHazard(1, 0.0, 0.0, "tether_trap", radius=60.0, damage=10.0, owner_id=1)
    world.arena.hazards.append(trap)

    action = Action(ball1, world)

    action.execute("idle", 0.5)

    # Tether trap pulls at 20.0 * delta = 20.0 * 0.5 = 10.0
    # Expected x = 30.0 - 10.0 = 20.0

    print(f"Ball x is {ball1.x}")
    assert ball1.x < 30.0

    has_event = False
    for event in world.events:
        if event['type'] == 'visual_effect' and event['effect'] == 'tether_link':
            has_event = True
    assert has_event
