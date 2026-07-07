import pytest
from system.profile import ProfileManager
from ai.action import Action
import os

class MockBall:
    def __init__(self, id, ball_type, x, y):
        self.id = id
        self.ball_type = ball_type
        self.x = x
        self.y = y
        self.hp = 100
        self.team = "Red"
        self.inventory = []
        self.alive = True

class MockWorld:
    def __init__(self):
        self.events = []
        self.profile_manager = ProfileManager("test_n_reveal.json")
        self.balls = []

def test_nemesis_reveal_passive():
    world = MockWorld()
    ball = MockBall(1, "basic", 0, 0)
    enemy = MockBall(2, "nemesis_class", 100, 100)
    world.balls = [ball, enemy]

    # Establish nemesis relationship
    world.profile_manager.add_kill(ball.ball_type, enemy.ball_type)
    world.profile_manager.add_kill(ball.ball_type, enemy.ball_type)
    assert world.profile_manager.is_nemesis(ball.ball_type, enemy.ball_type)

    action = Action(ball, world)

    # 1. Not triggered on first tick (timer starts at 5.0, becomes 4.0)
    action.execute("none", 1.0)
    assert getattr(ball, "nemesis_reveal_timer", 5.0) == 4.0
    found = any(e["type"] == "nemesis_compass" for e in world.events)
    assert not found

    # 2. Trigger after timer depletes
    action.execute("none", 4.0)
    assert getattr(ball, "nemesis_reveal_timer", 5.0) == 5.0

    # Verify events
    found_compass = False
    found_visual = False
    for e in world.events:
        if e["type"] == "nemesis_compass":
            found_compass = True
            assert e["data"]["target_x"] == 100.0
            assert e["data"]["target_y"] == 100.0
            assert e["data"]["owner_id"] == 1
        elif e["type"] == "visual_effect":
            found_visual = True
            assert e["data"]["type"] == "line"
            assert e["data"]["tx"] == 100.0
            assert e["data"]["ty"] == 100.0

    assert found_compass
    assert found_visual

    if os.path.exists("test_n_reveal.json"):
        os.remove("test_n_reveal.json")
