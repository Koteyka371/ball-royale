import pytest
from ai.action import Action

class MockHazard:
    def __init__(self, x, y, radius, kind):
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.damage = 0.0

class MockArena:
    def __init__(self):
        self.hazards = [MockHazard(100, 100, 50, "mirage_field")]

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.next_id = 1000

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 100
        self.y = 100
        self.hp = 100
        self.max_hp = 100
        self.speed = 10
        self.alive = True
        self.mirage_cooldown = 0.0

def test_mirage_field_spawns_clones():
    ball = MockBall()
    world = MockWorld()
    world.balls.append(ball)

    action = Action(ball, world)
    action.execute("flee", 0.1)

    # Should have original ball + 2 clones
    assert len(world.balls) == 3

    clones = [b for b in world.balls if getattr(b, "is_hologram", False)]
    assert len(clones) == 2

    for clone in clones:
        assert clone.hp == 1.0
        assert clone.max_hp == 1.0
        assert clone.hologram_timer == 3.0
        assert clone.clone_owner == 1

    assert ball.mirage_cooldown > 0.0

def test_mirage_field_cooldown():
    ball = MockBall()
    ball.mirage_cooldown = 1.0
    world = MockWorld()
    world.balls.append(ball)

    action = Action(ball, world)
    action.execute("flee", 0.1)

    # Should not spawn clones because cooldown is active
    assert len(world.balls) == 1
    assert pytest.approx(ball.mirage_cooldown) == 0.9
