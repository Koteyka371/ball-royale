import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()
    def get_nearby_entities(self, ball, radius):
        return {"enemies": [b for b in self.balls if getattr(b, "team", "") != ball.team], "allies": []}

class MockBall:
    def __init__(self, id, team):
        self.id = id
        self.team = team
        self.x = 0
        self.y = 0
        self.alive = True
        self.ball_type = "base"
        self.skill_timer = 0
        self.active_skill = "mind_control"
        self.perception_radius = 500

    def use_skill(self):
        pass

def test_mind_control():
    w = MockWorld()
    b1 = MockBall(1, "team1")
    b2 = MockBall(2, "team2")

    b1.x = 0
    b1.y = 0
    b2.x = 50
    b2.y = 0

    w.balls = [b1, b2]

    a = Action(b1, w)

    # Mock particle spawn to avoid AttributeError
    a._spawn_particles = lambda x, y, kind: None

    # Use mind control skill
    a._use_skill()

    assert getattr(b2, "is_mind_controlled", False)
    assert b2.team == "team1"
    assert getattr(b2, "original_team", "") == "team2"

    # Fast forward time
    a2 = Action(b2, w)
    a2.execute("idle", 6.0)

    assert not getattr(b2, "is_mind_controlled", False)
    assert b2.team == "team2"
