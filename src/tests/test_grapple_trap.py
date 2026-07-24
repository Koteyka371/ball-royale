import pytest
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.balls = []

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
        self.hp = 100.0
        self.alive = True
        self.inventory = []
        self.stun_timer = 0.0

def test_grapple_trap_pulls_and_roots():
    world = MockWorld()
    ball1 = MockBall(2, 100, 100) # The trigger ball
    world.balls = [ball1]

    # Initial distance from 100,100 to 0,0 is ~141.4. Trigger range is 200.
    trap = MockHazard(1, 0, 0, "grapple_trap", radius=40.0, owner_id=1)
    world.arena.hazards.append(trap)

    action = Action(ball1, world)

    action.execute("idle", 0.1)

    # Should pull closer
    assert ball1.x < 100.0
    assert ball1.y < 100.0
    assert trap.duration == 10.0
    assert ball1.stun_timer == 0.0

    # There should be visual effects
    assert any(e['type'] == 'visual_effect' and e['data']['type'] == 'line' for e in world.events)

    # Move ball1 inside root trigger radius (radius 10 + 40 * 0.25 = 20)
    ball1.x = 10
    ball1.y = 10
    ball1.stun_timer = 0.0

    action.execute("idle", 0.1)

    # Should root for 2 seconds and destroy trap
    assert ball1.stun_timer >= 2.0
    assert trap.duration == 0.0

if __name__ == "__main__":
    pytest.main(["-v", "test_grapple_trap.py"])
