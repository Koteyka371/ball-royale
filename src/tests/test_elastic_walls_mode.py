import pytest
from ai.game_modes import GAME_MODES
from ai.action import Action
import math

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.vx = 100
        self.vy = 0
        self.speed = 100
        self.max_speed = 200
        self.base_max_speed = 200
        self.id = "p1"
        self.elastic_bounce_timer = 0.0

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

    def clamp_position(self, x, y, radius):
        bounced = False
        nx, ny = x, y
        if x < radius:
            nx = radius
            bounced = True
        elif x > self.width - radius:
            nx = self.width - radius
            bounced = True

        if y < radius:
            ny = radius
            bounced = True
        elif y > self.height - radius:
            ny = self.height - radius
            bounced = True

        return nx, ny, bounced

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.width = 1000
        self.height = 1000
        self.balls = []
        self.game_mode = GAME_MODES["elastic_walls"]

def test_elastic_walls_bounce():
    mode = GAME_MODES["elastic_walls"]
    assert mode.name == "Elastic Walls"

    world = MockWorld()

    # Place a ball out of bounds to trigger bounce
    ball = MockBall(1010, 500)
    world.balls.append(ball)

    action = Action(ball, world)

    # Call _clamp_position directly to simulate bounce in the tick loop
    bounced = action._clamp_position()
    assert bounced is True

    # Verify the timer was set
    assert ball.elastic_bounce_timer == 2.0

    # Call mode tick
    mode.tick(world, [ball], delta=0.1)

    # Verify timer decremented and max speed increased
    assert math.isclose(ball.elastic_bounce_timer, 1.9)
    assert ball.max_speed == 300.0 # 200 * 1.5

    # Fast forward time
    ball.elastic_bounce_timer = 0.05
    mode.tick(world, [ball], delta=0.1)

    # Verify timer ran out and max speed returned to normal
    assert ball.elastic_bounce_timer < 0.0
    assert ball.max_speed == 200.0
