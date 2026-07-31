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
        self.radius = 10.0
        self.hp = 100.0
        self.alive = True
        self.inventory = []
        self.damage = 10.0

def test_deployable_pull_trap():
    world = MockWorld()
    ball1 = MockBall(2, 50, 50) # The trigger ball
    owner_ball = MockBall(1, 0, 0) # The owner ball
    world.balls = [owner_ball, ball1]

    trap = MockHazard(1, 10, 10, "deployable_pull_trap", radius=60.0, damage=10.0, owner_id=1)
    world.arena.hazards.append(trap)

    action = Action(ball1, world)

    # Initial distance from 50,50 to 10,10 is ~56.5 which is < 60
    # Should get pulled but not detonated (detonation is < 20)
    action.execute("idle", 0.016)

    assert trap.duration == 10.0
    assert ball1.x < 50.0 and ball1.y < 50.0
    assert ball1.hp == 100.0 # does no tick damage, only explosion damage

    # Move ball1 inside explosion trigger radius (dist < 10 + 10 = 20)
    ball1.x = 10
    ball1.y = 15
    ball1.hp = 100.0

    action.execute("idle", 0.016)

    # Should take explosion damage (60)
    assert ball1.hp <= 40.0
    assert trap.duration == 0.0 # Exploded

if __name__ == "__main__":
    pytest.main(["-v", "src/ai/test_deployable_pull_trap.py"])
