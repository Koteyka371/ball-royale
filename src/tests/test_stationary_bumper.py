import pytest
from ai.action import Action
from arena.procedural_arena import Hazard
import math
import random

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.width = 1000
        self.height = 1000
        self.boundary_offsets = {"top":0,"bottom":0,"left":0,"right":0}
        self.platforms = []

class MockWorld:
    def __init__(self, arena, balls):
        self.arena = arena
        self.balls = balls
        self.events = []
        self.projectiles = []
        self.tick = 0

class MockBall:
    def __init__(self, bid, x, y):
        self.id = bid
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.alive = True
        self.ball_type = "player"
        self.hp = 100.0
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.base_speed = 50.0
        self.speed = 50.0
        self.mass = 1.0
        self.base_mass = 1.0
        self.team = "blue"

def test_stationary_bumper():
    random.seed(42)
    ball = MockBall(1, 100.0, 100.0)
    bumper = Hazard(1, 105.0, 105.0, 20.0, "stationary_bumper", 0.0)
    world = MockWorld(MockArena([bumper]), [ball])
    action = Action(ball, world)

    ball.vx = 0.0
    ball.vy = 0.0

    action.execute("idle", 0.016)

    # Ball should be knocked back significantly
    assert abs(ball.vx) > 500.0 or abs(ball.vy) > 500.0
    print(f"Stationary bumper: vx={ball.vx}, vy={ball.vy}")

if __name__ == '__main__':
    test_stationary_bumper()
