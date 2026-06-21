import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.action import Action
from ai.decision import Decision

class MockEntity:
    def __init__(self, x, y, hp=100.0, alive=True, ball_type="enemy"):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp
        self.alive = alive
        self.ball_type = ball_type

class MockBall:
    def __init__(self, x=50, y=50, speed=10):
        self.current_action = None
        self.x = x
        self.y = y
        self.speed = speed
        self.ball_type = "mock_ball"
        self.alive = True
        self.personality = "scout"

class MockWorld:
    def __init__(self):
        self.entities = []

    def get_nearby_entities(self, ball, radius):
        return {
            "enemies": [e for e in self.entities if e.ball_type == "enemy"],
            "allies": [e for e in self.entities if e.ball_type == "ally"],
            "boosters": [e for e in self.entities if e.ball_type == "booster"]
        }

def test_target_weak_action():
    ball = MockBall(x=100, y=100)
    world = MockWorld()

    # e1 is strong
    e1 = MockEntity(x=100, y=200, hp=200.0)

    # e2 is weak, but further away
    e2 = MockEntity(x=200, y=100, hp=50.0)

    # e3 is medium
    e3 = MockEntity(x=100, y=0, hp=100.0)

    world.entities = [e1, e2, e3]

    action = Action(ball, world)
    action.execute("target_weak", 0.1)

    # Should chase e2 (x=200), meaning moving right (x > 100)
    assert ball.x > 100
    assert abs(ball.y - 100) < 1.0

def test_target_weak_decision():
    ball = MockBall()
    ball.ball_type = "scout"
    ball.difficulty = "hard" # disable random chance
    ball.skill_timer = 10.0 # disable skill
    decision = Decision(ball, MockWorld())

    perception_data = {
        "threat_level": 0.2, # low threat
        "opportunity_level": 0.8, # high opportunity
        "enemies": [MockEntity(0, 0)],
        "allies": [],
        "boosters": []
    }

    action = decision.choose_action(perception_data, "calm")
    assert action == "target_weak"
