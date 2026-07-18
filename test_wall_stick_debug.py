import sys
from ai.action import Action
import math

class MockBall:
    def __init__(self, x=500.0, y=500.0, vx=100.0, vy=0.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = 10.0
        self.alive = True
        self.is_hologram = False
        self.wall_stick_timer = 0.0
        self.is_stunned = False

class MockWorld:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.balls = []

world = MockWorld()
ball = MockBall(x=995.0, vx=100.0)
world.balls.append(ball)

action = Action(ball, world)
action.execute("target_weak", 0.1)

print("First tick wall_stick_timer:", ball.wall_stick_timer)
old_x = ball.x
action.execute("target_weak", 0.5)

print("Second tick wall_stick_timer:", ball.wall_stick_timer)
print("Second tick x:", ball.x, "old_x:", old_x)
