import sys
import os
sys.path.insert(0, os.path.abspath('src'))
from ai.action import Action

class MockBall:
    def __init__(self, x=0, y=0, radius=10.0, hp=0.0, alive=False):
        self.id = 999
        self.team = "test_team"
        self.ball_type = "basic"
        self.x = x
        self.y = y
        self.radius = radius
        self.hp = hp
        self.alive = alive
        self.speed = 10.0
        self.vx = 0
        self.vy = 0

class MockHazard:
    def __init__(self, x=10, y=0, radius=10.0):
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = "mud"

class MockArena:
    def __init__(self):
        self.hazards = [MockHazard(x=10, y=0)]

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []

def test_ghost_player():
    ball = MockBall(x=0, y=0, hp=0, alive=False)
    world = MockWorld()
    world.balls = [ball]
    action = Action(ball, world)

    # Tick 1: transform to ghost
    action.execute("idle", 1.0)
    assert ball.ball_type == "ghost"

    # Tick 2: ghost behavior
    action.execute("idle", 1.0)
    assert ball.x > 0
    assert world.arena.hazards[0].x > 10
