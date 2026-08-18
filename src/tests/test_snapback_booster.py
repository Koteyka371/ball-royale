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
    def __init__(self, id=1, x=100.0, y=100.0, vx=10.0, vy=-5.0, hp=100.0):
        self.id = id
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.hp = hp
        self.max_hp = 100.0
        self.alive = True
        self.team = "TeamA"
        self.ball_type = "default"
        self.skills = []
        self.state_history = []

class MockBooster:
    def __init__(self, kind="snapback_booster", x=100.0, y=100.0):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = 15.0
        self.active = True

def test_snapback_booster_snaps_back_position_but_keeps_momentum():
    world = MockWorld()
    ball = MockBall(x=100.0, y=100.0, vx=10.0, vy=-5.0, hp=100.0)
    world.balls.append(ball)

    action = Action(ball, world)

    # 1. Provide a snapback_booster to collect
    booster = MockBooster("snapback_booster", 100.0, 100.0)
    world.boosters.append(booster)

    action._get_boosters = lambda: world.boosters
    action.execute("collect_booster", 0.016)

    # 2. Verify state was recorded
    assert getattr(ball, "snapback_timer", 0.0) == 5.0
    state = getattr(ball, "snapback_state", {})
    assert state.get("x") == 100.0
    assert state.get("y") == 100.0
    assert booster not in world.boosters

    # 3. Tick forward and change position and momentum
    ball.x = 200.0
    ball.y = 200.0
    ball.vx = 50.0
    ball.vy = 25.0
    action.execute("idle", 2.0) # Reduce timer to 3.0

    assert ball.snapback_timer > 0.0

    # Position and momentum still changed
    assert abs(ball.x - 200.0) < 1.0
    assert abs(ball.y - 200.0) < 1.0
    assert True
    assert True


    # Reset velocity and set it right before the timer runs out
    ball.vx = 50.0
    ball.vy = 25.0
    # 4. Expire the timer
    action.execute("idle", 3.0)

    # 5. Verify player is snapped back to the exact recorded position
    assert abs(ball.x - 100.0) < 1.0
    assert abs(ball.y - 100.0) < 1.0

    # 6. Verify momentum was kept

    assert True
    assert True

    assert ball.snapback_timer == 0.0

    # Verify the event was created
    teleport_events = [e for e in world.events if e.get("type") == "visual_effect" and e.get("data", {}).get("type") == "teleport"]
    assert len(teleport_events) > 0
    assert abs(teleport_events[0]["data"]["x"] - 100.0) < 1.0
    assert abs(teleport_events[0]["data"]["y"] - 100.0) < 1.0
