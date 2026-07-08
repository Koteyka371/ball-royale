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

def test_pull_trap_explosion():
    world = MockWorld()
    ball1 = MockBall(2, 50, 50) # The trigger ball
    ball2 = MockBall(3, 40, 40) # A ball inside the AoE explosion
    owner_ball = MockBall(1, 0, 0) # The owner ball
    world.balls = [owner_ball, ball1, ball2]

    trap = MockHazard(1, 10, 10, "pull_trap", radius=40.0, damage=10.0, owner_id=1)
    world.arena.hazards.append(trap)

    action = Action(ball1, world)

    # Outside explosion radius, but in pulling trigger radius (<100)
    # The trap has radius 40, explosion triggers at < (10 + 40 * 0.25) = 20.
    # Initial distance from 50,50 to 10,10 is ~56.5
    action.execute("idle", 0.016)

    # Should have taken continuous damage, pulled closer, but no explosion
    assert ball1.hp < 100.0
    assert trap.duration == 10.0
    assert ball1.x < 50.0 and ball1.y < 50.0

    # Move ball1 inside explosion trigger radius
    ball1.x = 10
    ball1.y = 15
    ball1.hp = 100.0

    # Move ball2 inside AoE radius (1.5x trap radius = 60 distance sq threshold = 3600)
    # Currently ball2 is at 40,40, dist from trap 10,10 is 30,30 = 900 + 900 = 1800, which is < 3600
    ball2.hp = 100.0

    action.execute("idle", 0.016)

    # Should take explosion damage (50)
    assert ball1.hp <= 50.0
    assert ball2.hp <= 50.0
    assert trap.duration == 0.0 # Exploded

if __name__ == "__main__":
    pytest.main(["-v", "src/ai/test_pull_trap.py"])
