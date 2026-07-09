import sys
import os
import math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []

class MockBall:
    def __init__(self, x, y):
        self.id = 1
        self.ball_type = "warrior"
        self.alive = True
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 100.0
        self.damage = 10.0

class MockHazard:
    def __init__(self, x, y, radius, kind):
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.vx = 50.0
        self.vy = 0.0

def test_windstorm_tornado_mechanics():
    mode = GAME_MODES["windstorm"]
    world = MockWorld()

    # Place a ball outside tornado, but close enough to be pulled
    ball = MockBall(100.0, 100.0)

    # Place tornado
    tornado = MockHazard(150.0, 100.0, 30.0, "tornado")
    world.arena.hazards.append(tornado)

    initial_ball_x = ball.x
    initial_tornado_x = tornado.x

    # Tick mode
    mode.tick(world, [ball], 0.1)

    # Tornado should wander (vx = 50, dt = 0.1 -> x + 5)
    assert tornado.x > initial_tornado_x

    # Ball should be pulled towards tornado (x should increase)
    assert ball.x > initial_ball_x

    # Now place ball inside tornado to test scramble
    ball.x = tornado.x
    ball.y = tornado.y
    ball.vx = 0.0
    ball.vy = 0.0

    mode.tick(world, [ball], 0.1)

    # Ball vx and vy should be scrambled
    assert ball.vx != 0.0 or ball.vy != 0.0

if __name__ == '__main__':
    test_windstorm_tornado_mechanics()
    print("Tests passed.")
