import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.game_modes import ZoneControlMode
from ai.decision import Decision

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.game_mode = ZoneControlMode()

class MockBall:
    def __init__(self, id, ball_type="warrior"):
        self.id = id
        self.ball_type = ball_type
        self.team = ball_type
        self.alive = True
        self.x = 500
        self.y = 500
        self.hp = 100
        self.max_hp = 100
        self.score = 0
        self.difficulty = "medium"
        self.personality = "warrior"
        self.speed = 10
        self.damage = 10

def test_zone_control_mode():
    mode = ZoneControlMode()
    world = MockWorld()
    balls = [MockBall(1, "warrior"), MockBall(2, "scout")]

    mode.setup(world, balls)

    # Tick should increase points
    mode.tick(world, balls, 0.5)
    assert mode.teams_scores["warrior"] == 1
    assert mode.teams_scores["scout"] == 1

    # Move scout out of zone
    balls[1].x = 100
    balls[1].y = 100

    mode.tick(world, balls, 0.5)
    assert mode.teams_scores["warrior"] == 2
    assert mode.teams_scores["scout"] == 1

def test_zone_control_decision():
    world = MockWorld()
    ball = MockBall(1, "warrior")
    decision = Decision(ball, world)

    perception_data = {
        "danger_level": 0.0,
        "threat_level": 0.0,
        "opportunity_score": 0.0,
        "opportunity_level": 0.0,
        "enemies": [],
        "allies": [],
        "boosters": [],
        "distances": {},
        "coach_strategy": ""
    }

    # In zone control, it should prioritize hold_zone
    action = decision.choose_action(perception_data, "calm")
    assert action == "hold_zone"
