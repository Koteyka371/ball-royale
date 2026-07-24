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
    def __init__(self, id, x, y, kind, radius=40.0, owner_id=1):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = radius
        self.owner_id = owner_id
        self.duration = 10.0

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 10.0
        self.stun_timer = 0.0
        self.speed = 0.0
        self.base_speed = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.is_intangible = False
        self.bounces_left = 0
        self.max_hp = 100.0

def test_grapple_trap():
    world = MockWorld()
    ball = MockBall(2, 100, 100)
    world.balls = [ball]

    trap = MockHazard(1, 0, 0, "grapple_trap", radius=40.0, owner_id=1)
    world.arena.hazards.append(trap)

    action = Action(ball, world)
    action.execute("idle", 0.1)

    # With speed 0, wander won't push it away. The pull is 200 * 0.1 = 20
    # Initial is 100, 100. Should be pulled to ~85.8, 85.8
    assert ball.x < 100
    assert ball.y < 100
    assert trap.duration == 10.0
    assert ball.stun_timer == 0.0

    ball.x = 10
    ball.y = 10

    action.execute("idle", 0.1)

    assert ball.stun_timer == 2.0
    assert trap.duration == 0.0

if __name__ == "__main__":
    pytest.main(["-v", "tests/test_grapple_trap.py"])
