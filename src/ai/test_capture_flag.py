import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.game_modes import CaptureTheFlagMode
from ai.action import Action
from ai.decision import Decision

class MockBall:
    def __init__(self, id, ball_type="warrior", alive=True, team="Red"):
        self.id = id
        self.ball_type = ball_type
        self.alive = alive
        self.team = team
        self.max_hp = 100
        self.hp = 100
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.has_flag = False
        self.speed = 2.0
        self.skill_timer = 0.0
        self.attack_timer = 0.0
        self.attack_range = 50.0

class MockBooster:
    def __init__(self, id, is_flag=False, team="Red", x=0, y=0):
        self.id = id
        self.is_flag = is_flag
        self.team = team
        self.x = x
        self.y = y

class MockWorld:
    def __init__(self):
        self.boosters = []
        self.scores = {"Red": 0, "Blue": 0}

def test_capture_the_flag_setup():
    mode = CaptureTheFlagMode()
    world = MockWorld()
    balls = [MockBall(1), MockBall(2), MockBall(3), MockBall(4)]

    mode.setup(world, balls)

    assert hasattr(world, "flags")
    assert "Red" in world.flags
    assert "Blue" in world.flags
    assert balls[0].team == "Red"
    assert balls[3].team == "Blue"

def test_escort_behavior():
    action = Action(MockBall(1, team="Red"), MockWorld())
    ally_with_flag = MockBall(2, team="Red")
    ally_with_flag.has_flag = True
    ally_with_flag.x = 100
    ally_with_flag.y = 100

    # Mocking perception to return our ally
    action.world.get_nearby_entities = lambda *args: {"allies": [ally_with_flag], "enemies": [], "boosters": [], "traps": []}

    # execute escort
    action.execute("escort", 1.0)

    # Should move toward ally_with_flag
    assert action.ball.x > 0 or action.ball.y > 0

def test_intercept_behavior():
    action = Action(MockBall(1, team="Red"), MockWorld())
    enemy_with_flag = MockBall(2, team="Blue")
    enemy_with_flag.has_flag = True
    enemy_with_flag.x = 100
    enemy_with_flag.y = 100

    # Mocking perception to return enemy flag carrier
    action.world.get_nearby_entities = lambda *args: {"allies": [], "enemies": [enemy_with_flag], "boosters": [], "traps": []}

    # execute intercept
    action.execute("intercept", 1.0)

    # Should move toward enemy_with_flag
    assert action.ball.x > 0 or action.ball.y > 0

def test_decision_prioritizes_flags():
    ball = MockBall(1, team="Red")
    world = MockWorld()
    decision = Decision(ball, world)

    ally = MockBall(2, team="Red")
    ally.has_flag = True

    enemy = MockBall(3, team="Blue")
    enemy.has_flag = True

    perception_data = {
        "allies": [ally],
        "enemies": [enemy],
        "boosters": [],
        "threat_level": 0.5,
        "opportunity_score": 0.5,
        "coach_strategy": ""
    }

    best_action = decision.choose_action(perception_data, "calm")

    # It should prioritize escort or intercept due to +800 bonuses
    assert best_action in ["escort", "intercept", "use_skill"]
