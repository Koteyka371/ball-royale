import pytest
import sys
sys.path.insert(0, "src")

from ai.action import Action

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100.0
        self.alive = True
        self.ball_type = "player"
        self.team = "A"

class MockEntity:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.ball_type = "booster"

class MockWorld:
    def __init__(self):
        self.events = []
        self.arena = type('Arena', (), {'hazards': []})()
        self.boosters = []

def test_instant_rewind_booster():
    ball = MockBall("b1", 10.0, 20.0)
    world = MockWorld()

    # State history mock setup
    ball.state_history = [
        {"x": 10.0, "y": 20.0, "hp": 100.0},
        {"x": 15.0, "y": 25.0, "hp": 90.0},
        {"x": 30.0, "y": 40.0, "hp": 50.0}
    ]
    # Set ball position as current
    ball.x = 30.0
    ball.y = 40.0
    ball.hp = 50.0

    booster = MockEntity(30.0, 40.0, "instant_rewind_booster")
    world.boosters = [booster]
    world.arena.hazards = [booster]

    action = Action(ball, world)

    # Mock finding the booster
    action._get_boosters = lambda: [booster]
    action._get_enemies = lambda: []

    action.execute("collect_booster", 1.0)

    assert len(world.boosters) == 0
    assert len(world.arena.hazards) == 0
    assert ball.x == 10.0
    assert ball.y == 20.0
    assert ball.hp == 100.0

    # Check if event was fired
    rewind_events = [e for e in world.events if e["type"] == "time_rewind"]
    assert len(rewind_events) == 1
    assert rewind_events[0]["data"]["id"] == "b1"
