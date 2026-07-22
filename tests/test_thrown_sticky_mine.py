import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/ai')))
from action import Action

class MockWorld:
    def __init__(self):
        self.arena = type("Arena", (), {"hazards": []})
        self.balls = []
        self.events = []
        self.boosters = []

class MockBall:
    def __init__(self, x, y, id):
        self.x = x
        self.y = y
        self.id = id
        self.hp = 150
        self.alive = True
        self.radius = 10
        self.team = id
        self._base_speed_set = True
        self.base_speed = 2.0

def test_thrown_sticky_mine():
    world = MockWorld()
    b1 = MockBall(0, 0, 1)
    b2 = MockBall(30, 0, 2)
    world.balls = [b1, b2]

    action = Action(b1, world)
    action.ball.skill = "throw_sticky_mine"
    action.execute("use_skill", 0.016)

    assert len(world.arena.hazards) == 1
    mine = world.arena.hazards[0]
    assert mine.kind == "thrown_sticky_mine"

    for _ in range(10):
        action.execute("idle", 0.016)
        if getattr(mine, "attached_id", None) == 2:
            break

    assert getattr(mine, "attached_id", None) == 2

    for _ in range(200):
        action.execute("idle", 0.016)

    assert len(world.arena.hazards) == 0
    assert b2.hp < 150
