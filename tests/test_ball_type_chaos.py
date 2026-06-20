import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_types_chaos import Chaos

class MockEntity:
    def __init__(self, x=0, y=0, radius=10):
        self.x = x
        self.y = y
        self.radius = radius

def test_chaos_instantiation():
    ball = Chaos(ball_id=1)
    assert ball.id == 1
    assert ball.hp == 100
    assert ball.max_hp == 100
    assert ball.SPEED == 3.0
    assert ball.difficulty == "chaos"
    assert ball.BALL_TYPE == "chaos"

def test_chaos_flee():
    ball = Chaos(ball_id=1)
    ball.flee(0.1)
    assert ball.current_action == "flee"

def test_chaos_attack():
    ball = Chaos(ball_id=1, x=0, y=0)
    target = MockEntity(x=100, y=100)

    # Store initial x/y to verify movement
    initial_x, initial_y = ball.x, ball.y
    ball.attack(0.1, target)

    assert ball.current_action == "attack"
    # Verify that it moved (we won't check exact coordinates due to randomness)
    assert ball.x != initial_x or ball.y != initial_y

def test_chaos_skill():
    ball = Chaos(ball_id=1)
    assert ball.use_skill() is True
    assert ball.skill_timer == 2.0
    assert ball.use_skill() is False
