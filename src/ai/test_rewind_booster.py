import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from ai.action import Action
import pytest

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.time = 0.0
        self.boosters = []
        self.arena = MockArena()

class MockBall:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.hp = 100.0
        self.skill_timer = 5.0
        self.alive = True
        self.speed = 0.0
        self.ball_type = "enemy"
        self.inventory = []
        self.perception_radius = 100
        self.personality = "idle"

def test_rewind_booster_mechanic():
    world = MockWorld()
    ball = MockBall()
    action = Action(ball, world)

    ball.rewind_booster_active = True
    world.time = 1.0
    action.execute("idle", 0.1)

    assert len(ball.rewind_history) == 1
    assert ball.rewind_history[0][:4] == (1.0, 0.0, 0.0, 100.0)

    # Move and take damage
    ball.x = 10.0
    ball.y = 10.0
    ball.hp = 50.0
    world.time = 2.0
    action.execute("idle", 0.1)

    # Die
    ball.x = 20.0
    ball.y = 20.0
    ball.hp = -10.0
    world.time = 2.5
    action.execute("idle", 0.1)

    # Should rewind to state at time 1.0
    assert ball.hp == 100.0
    assert ball.x == 0.0
    assert ball.y == 0.0
    assert not ball.rewind_booster_active
    assert len(ball.rewind_history) == 0
