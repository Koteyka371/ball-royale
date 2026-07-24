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

def test_grapple_trap_pull_and_root():
    world = MockWorld()
    ball = MockBall(2, 100, 100)
    world.balls = [ball]

    # Trap at 0, 0
    trap = MockHazard(1, 0, 0, "grapple_trap", radius=40.0, owner_id=1)
    world.arena.hazards.append(trap)

    action = Action(ball, world)

    # Initial distance is sqrt(20000) ~ 141.4, which is < 200 (dist_sq < 40000)
    # The trap should reel in the ball
    action.execute("idle", 0.1)

    assert ball.x < 100
    assert ball.y < 100
    assert trap.duration == 10.0
    assert ball.stun_timer == 0.0

    # Ensure a line event was created
    assert any(e.get("type") == "visual_effect" and e.get("data", {}).get("type") == "line" for e in world.events)

    # Move ball into rooting range (radius + hazard.radius * 0.25 = 10 + 10 = 20)
    ball.x = 10
    ball.y = 10
    # Dist is sqrt(200) ~ 14.1 < 20

    action.execute("idle", 0.1)

    # Ball should be rooted and trap destroyed
    assert ball.stun_timer == 2.0
    assert trap.duration == 0.0

if __name__ == "__main__":
    pytest.main(["-v", "src/tests/test_grapple_trap.py"])
