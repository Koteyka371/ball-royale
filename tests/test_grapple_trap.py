import pytest
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []

class MockArena:
    def __init__(self):
        self.hazards = []

class MockHazard:
    def __init__(self, id, x, y, kind, radius=40.0, damage=10.0, owner_id=1):
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
        self.radius = 10.0
        self.hp = 100.0
        self.alive = True
        self.inventory = []
        self.damage = 10.0
        self.stun_timer = 0.0
        self.speed = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.is_intangible = False
        self.bounces_left = 0
        self.max_hp = 100.0

def test_grapple_trap():
    world = MockWorld()
    ball1 = MockBall(2, 50, 50)
    world.balls = [ball1]

    trap = MockHazard(1, 10, 10, "grapple_trap", radius=20.0, damage=10.0, owner_id=1)
    world.arena.hazards.append(trap)

    action = Action(ball1, world)

    # Trigger the pull
    action.execute("idle", 0.016)

    assert ball1.x < 50.0 and ball1.y < 50.0
    assert trap.duration == 10.0
    assert ball1.stun_timer == 0.0

    # Center triggers stun
    ball1.x = 10.0
    ball1.y = 15.0

    action.execute("idle", 0.016)

    assert ball1.stun_timer >= 2.0
    assert trap.duration == 0.0

if __name__ == "__main__":
    pytest.main(["-v", "src/ai/test_grapple_trap.py"])
