import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.action import Action

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

class MockWorld:
    def __init__(self):
        self.events = []
        self.tick = 0
        self.balls = []

def test_survival_rewind_records_state_and_revives():
    world = MockWorld()
    ball = MockBall(x=50.0, y=50.0, hp=100.0)
    world.balls.append(ball)

    action = Action(ball, world)

    # 1. Use the skill
    ball.skill = "survival_rewind"
    action.execute("use_skill", 0.016)

    # Verify state was recorded
    assert getattr(ball, "survival_rewind_timer", 0.0) == 5.0
    state = getattr(ball, "survival_rewind_state", {})
    assert state.get("x") == 50.0
    assert state.get("y") == 50.0
    assert state.get("hp") == 100.0

    # 2. Tick forward a bit and change state
    ball.x = 200.0
    ball.y = 200.0
    ball.hp = 80.0
    action.execute("idle", 2.0) # Reduce timer to 3.0

    assert ball.survival_rewind_timer > 0.0

    # 3. Simulate taking lethal damage
    ball.hp = 0.0

    action.execute("idle", 0.016)

    # 4. Verify player is revived to the exact recorded state
    assert ball.alive == True
    assert ball.x == 50.0
    assert ball.y == 50.0
    assert ball.hp == 100.0
    assert ball.survival_rewind_timer == 0.0

    # Verify the event was created
    rewind_events = [e for e in world.events if e.get("type") == "time_rewind"]
    assert len(rewind_events) > 0
    assert rewind_events[0]["data"]["id"] == ball.id

def test_survival_rewind_expires():
    world = MockWorld()
    ball = MockBall(x=50.0, y=50.0, hp=100.0)
    world.balls.append(ball)

    action = Action(ball, world)

    # 1. Use the skill
    ball.skill = "survival_rewind"
    action.execute("use_skill", 0.016)

    assert getattr(ball, "survival_rewind_timer", 0.0) == 5.0

    # 2. Tick forward beyond 5 seconds
    action.execute("idle", 6.0)

    assert ball.survival_rewind_timer <= 0.0

    # 3. Take lethal damage AFTER timer expires
    ball.hp = 0.0
    action.execute("idle", 0.016)

    # 4. Verify player dies and is NOT revived
    assert ball.hp == 0.0
    # Because action.execute doesn't manage ball.alive when hp <= 0 (unless specific mechanics do),
    # we just verify that it didn't revive us and set hp back to 100.0
    assert ball.hp == 0.0

    rewind_events = [e for e in world.events if e.get("type") == "time_rewind"]
    assert len(rewind_events) == 0
