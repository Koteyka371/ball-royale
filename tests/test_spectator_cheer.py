import pytest
from ai.action import Action
from ai.ball_types_spectator import Spectator

class MockArena:
    def __init__(self):
        self.hazards = []

    def clamp_position(self, x, y, r):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.boosters = []

    def get_nearby_entities(self, ball, radius):
        return {'boosters': [], 'hazards': [], 'enemies': [], 'allies': []}

class MockBall:
    def __init__(self, ball_id, ball_type):
        self.id = ball_id
        self.ball_type = ball_type
        self.team = "spectator"
        self.x = 0
        self.y = 0
        self.radius = 5
        self.cheer_points = 50
        self.skill_timer = 0
        self.perception_radius = 300

def test_spectator_cheer():
    world = MockWorld()
    ball = MockBall(1, "spectator")
    action = Action(ball, world)

    # Cheer confetti
    action.execute("cheer:confetti", 1.0)

    assert ball.cheer_points == 40
    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert hazard.kind == "confetti"
    assert hazard.damage == 0
    assert hazard.owner_id == ball.id

    # Cheer emote smile
    action.execute("cheer:emote_smile", 1.0)
    assert ball.cheer_points == 30
    assert len(world.arena.hazards) == 2
    assert world.arena.hazards[1].kind == "emote_smile"

def test_spectator_cheer_insufficient_points():
    world = MockWorld()
    ball = MockBall(2, "spectator")
    ball.cheer_points = 5
    action = Action(ball, world)

    # Not enough points
    action.execute("cheer:confetti", 1.0)

    assert ball.cheer_points == 5
    assert len(world.arena.hazards) == 0

def test_spectator_initialization():
    spec = Spectator(1)
    assert spec.cheer_points == 100

if __name__ == "__main__":
    pytest.main(["-v", __file__])
