import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.game_modes import TugOfWarMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []
        self.mutators = []

class MockBall:
    def __init__(self, team="Neutral", x=0, y=0, ball_type="basic"):
        self.team = team
        self.x = x
        self.y = y
        self.ball_type = ball_type
        self.alive = True
        self.radius = 10.0
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 10.0
        self.base_speed = 10.0
        self.max_hp = 100.0
        self.hp = 100.0

def test_bouncy_payload():
    mode = TugOfWarMode()
    world = MockWorld()
    world.mutators = ["bouncy_payload"]
    brawler = MockBall(ball_type="brawler", x=475.0, y=500.0)
    brawler.vx = 1000.0

    balls = [brawler, MockBall(ball_type="sniper", x=100.0, y=100.0)]
    mode.setup(world, balls)

    mode.tick(world, balls, 0.1)

    payload = balls[2]
    # Check if bouncy behavior was applied
    assert payload.vx == -15000.0
    assert payload.x == 950.0
