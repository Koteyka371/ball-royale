import math
from ai.game_modes import GameMode
from ai.action import Action
import random

class MockBall:
    def __init__(self, x=0, y=0, ball_type="warrior"):
        self.id = 1
        self.x = x
        self.y = y
        self.radius = 10
        self.speed = 10
        self.ball_type = ball_type
        self.mass = 1.0
        self.vx = 0.0
        self.vy = 0.0
        self.max_hp = 100
        self.hp = 100

class MockWorld:
    def __init__(self):
        self.balls = []
        self.is_reversed = False

def test_reverse_event_trigger():
    random.seed(42)
    mode = GameMode()
    world = MockWorld()
    mode.reverse_cooldown = 0.01

    triggered = False
    for _ in range(100):
        mode.tick(world, [], 0.02)
        if world.is_reversed:
            triggered = True
            break

    assert triggered

def test_action_reversal():
    ball = MockBall(100, 100)
    world = MockWorld()
    world.is_reversed = True

    class TestAction(Action):
        def _idle(self, delta):
            self.ball.x += 10
            self.ball.y += 10

    action = TestAction(ball, world)
    action.world.is_reversed = True
    action.execute("idle", 0.1)

    # Normally idle would move it +10, but reversed means it goes -10
    assert ball.x == 90
    assert ball.y == 90
