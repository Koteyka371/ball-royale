import pytest
from unittest.mock import MagicMock
from ai.action import Action

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 800
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []
        self.next_id = 999
        self.width = 1000
        self.height = 800

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": []}

class MockBall:
    def __init__(self, id, x, y, skill):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.skill = skill
        self.alive = True
        self.hp = 100
        self.max_hp = 100
        self.team = "blue"
        self.skill_timer = 0
        self.speed = 10
        self.damage = 10
        self.radius = 10

def test_perfect_mirror_clone_skill():
    world = MockWorld()
    ball = MockBall(1, 200, 300, "perfect_mirror")
    world.balls.append(ball)

    action = Action(ball, world)
    action.execute("use_skill", 1.0)

    # Check if clone is created
    assert len(world.balls) == 2
    clone = world.balls[1]

    assert clone.id != ball.id
    assert clone.owner_id == ball.id
    assert getattr(clone, "is_perfect_mirror", False) is True

    # Should be perfectly mirrored across center (1000, 800 arena)
    # x = 1000 - 200 = 800
    # y = 800 - 300 = 500
    assert clone.x == 800
    assert clone.y == 500

    # Now simulate tick for clone
    clone_action = Action(clone, world)
    clone_action.execute("idle", 1.0)

    assert clone.x == 800
    assert clone.y == 500

    # Move owner and check again
    ball.x = 100
    ball.y = 150
    ball.vx = 50
    ball.vy = -20
    clone_action.execute("idle", 1.0)

    assert clone.x == 900
    assert clone.y == 650
    assert clone.vx == -50
    assert clone.vy == 20
