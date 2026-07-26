import pytest
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.arena = type('Arena', (), {'hazards': []})()
        self.balls = []
        self.tick = 0

class MockHazard:
    def __init__(self, id, x, y, kind, radius=40.0, damage=10.0, owner_id=None):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = radius
        self.damage = damage
        self.owner_id = owner_id
        self.duration = 10.0
        self.active = True

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 20.0
        self.team = f"team_{id}"
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.ball_type = "normal"

def test_leech_seed_trap():
    world = MockWorld()
    ball1 = MockBall(1, 0, 0)
    ball2 = MockBall(2, 50, 0)
    world.balls = [ball1, ball2]

    # Owner is ball1
    trap = MockHazard(99, 50, 0, "leech_seed_trap", owner_id=1)
    world.arena.hazards.append(trap)

    action = Action(ball2, world)

    # Ball 2 triggers the trap
    action.execute("idle", 0.1)

    assert trap.duration == 0.0 # Destroyed
    assert getattr(ball2, "leech_seed_timer", 0.0) == 10.0
    assert getattr(ball2, "leech_seed_attacker_id", None) == 1

    # Now let's check if ball1 heals and ball2 takes damage
    ball1.hp = 50.0

    # Tick again to process leech_seed_timer
    action.execute("idle", 0.1)

    assert ball2.hp < 100.0
    assert ball1.hp > 50.0

if __name__ == "__main__":
    pytest.main(["-v", "src/ai/test_leech_seed_trap.py"])
