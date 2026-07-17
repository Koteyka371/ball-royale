import pytest
from ai.action import Action
from tests.test_action import MockBall, MockWorld

class MockBooster:
    def __init__(self, id, x, y, kind):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
    def get(self, key, default=None):
        return getattr(self, key, default)

def test_tornado_booster():
    ball = MockBall(1, 100, 100)
    ball.id = 1
    ball.team = 1
    enemy = MockBall(2, 120, 100)
    enemy.id = 2
    enemy.team = 2
    enemy.alive = True

    world = MockWorld()
    world.balls = [ball, enemy]
    world.hazards = []

    a = Action(ball, world)

    ball.tornado_booster_timer = 5.0
    a.execute("idle", 0.016)
    assert enemy.x < 120

    # Test mud immunity
    ball.tornado_booster_timer = 5.0
    class MockHazard:
        def __init__(self, x, y, kind):
            self.x = x
            self.y = y
            self.kind = kind
            self.radius = 50.0
            self.active = True

    world.arena = type('Arena', (), {'hazards': [MockHazard(100, 100, "mud_puddle")]})()

    a.execute("idle", 0.016)
    assert not getattr(ball, "is_in_mud", False)
