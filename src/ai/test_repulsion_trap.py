import pytest
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []

    def _deal_damage(self, owner, target):
        target.hp -= owner.damage

class MockArena:
    def __init__(self):
        self.hazards = []

    def clamp_position(self, x, y, radius):
        return x, y, False

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
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.hp = 100.0
        self.alive = True
        self.inventory = []
        self.damage = 10.0
        self.last_updated_tick = 0
        self.team = "A"

def test_repulsion_trap_explosion():
    world = MockWorld()
    ball1 = MockBall(2, 50, 50) # The trigger ball
    ball2 = MockBall(3, 40, 40) # A ball inside the AoE explosion
    owner_ball = MockBall(1, 0, 0) # The owner ball
    owner_ball.team = "B"
    ball1.team = "A"
    ball2.team = "A"
    world.balls = [owner_ball, ball1, ball2]

    trap = MockHazard(1, 10, 10, "repulsion_trap", radius=40.0, damage=0.0, owner_id=1)
    world.arena.hazards.append(trap)

    action = Action(ball1, world)

    action.execute("idle", 0.016)

    # Move ball1 inside trigger radius
    ball1.x = 20
    ball1.y = 20

    # Move ball2 inside AoE radius (3.0x trap radius = 120 distance sq threshold = 14400)
    # The hazard is at 10, 10. Max dist is 120. So 100, 100 is dist^2 = (90)^2 + (90)^2 = 8100 + 8100 = 16200. WAIT.
    # 16200 > 14400! So ball2 was NOT in the radius in my previous test!!!
    ball2.x = 60
    ball2.y = 60

    # Reset vx and vy to strictly 0
    ball1.vx = 0.0
    ball1.vy = 0.0
    ball2.vx = 0.0
    ball2.vy = 0.0

    action.execute("idle", 0.016)

    # Should take zero damage, get knocked back, and trap duration 0
    assert ball1.hp == 100.0
    assert ball2.hp == 100.0
    assert trap.duration == 0.0 # Exploded

    # Check that velocity has increased enormously
    assert abs(ball1.vx) > 1000.0 or abs(ball1.vy) > 1000.0

    # Note: since the hazard iteration is part of action.execute, ball2's hazard processing would have happened
    # but action.execute for ball1 doesn't update ball2's end-of-tick physics logic (like moving `_reflection_vx` to `vx`).
    # Let's manually trigger it for ball2, or just assert on `_reflection_vx`.
    assert abs(getattr(ball2, '_reflection_vx', ball2.vx)) > 1000.0 or abs(getattr(ball2, '_reflection_vy', ball2.vy)) > 1000.0

    assert getattr(ball1, 'is_frictionless', False) == True
    assert getattr(ball2, 'is_frictionless', False) == True

if __name__ == "__main__":
    pytest.main(["-v", "test_repulsion_trap.py"])
