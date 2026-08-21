import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.events = []
        self.tick = 0
        self.balls = []
        self.boosters = []
        self.arena = MockArena()

class MockBall:
    def __init__(self, id=1, x=100.0, y=100.0, hp=100.0):
        self.id = id
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = 100.0
        self.alive = True
        self.team = "TeamA"
        self.ball_type = "default"
        self.skills = []
        self.state_history = []
        self.radius = 10.0

class MockBooster:
    def __init__(self, kind="recall_booster", x=100.0, y=100.0):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = 15.0
        self.active = True

def test_recall_booster():
    world = MockWorld()
    ball = MockBall(x=100.0, y=100.0, hp=100.0)
    world.balls.append(ball)

    action = Action(ball, world)

    # 1. Provide a recall_booster to collect
    booster = MockBooster("recall_booster", 100.0, 100.0)
    world.boosters.append(booster)

    action._get_boosters = lambda: world.boosters
    action.execute("collect_booster", 0.016)

    # 2. Verify state was recorded
    assert getattr(ball, "recall_timer", 0.0) == 5.0
    state = getattr(ball, "recall_state", {})
    assert state.get("x") == 100.0
    assert state.get("y") == 100.0
    assert state.get("hp") == 100.0
    assert booster not in world.boosters

    # 3. Tick forward a bit and change state
    ball.x = 200.0
    ball.y = 200.0
    ball.hp = 80.0
    action.execute("idle", 2.0) # Reduce timer to 3.0

    assert ball.recall_timer > 0.0
    assert abs(ball.x - 200.0) < 1.0
    assert ball.hp == 80.0

    # 4. Tick forward remaining time
    action.execute("idle", 3.0)

    # 5. Verify player is reverted to the exact recorded state
    assert ball.alive == True
    assert abs(ball.x - 100.0) < 1.0
    assert abs(ball.y - 100.0) < 1.0
    assert ball.hp == 100.0
    assert getattr(ball, "recall_timer", 0.0) == 0.0

    # Verify the event was created
    rewind_events = [e for e in world.events if e.get("type") == "time_rewind"]
    assert len(rewind_events) > 0
    assert rewind_events[0]["data"]["id"] == ball.id
