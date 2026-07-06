import pytest
from ai.game_modes import GameMode

# Because we append DodgeballMode in src/ai/game_modes.py dynamically during plan
# We should import it carefully
import ai.game_modes as gm

def test_dodgeball_setup():
    mode = gm.DodgeballMode()
    class MockWorld:
        pass
    world = MockWorld()
    world.arena = type('Arena', (), {'width': 1000, 'height': 1000})()
    world.dead_balls = []

    class MockBall:
        def __init__(self):
            self.x = 0
            self.y = 0
            self.vx = 0
            self.vy = 0
            self.team = None
            self.alive = True
            self.ball_type = "normal"

    balls = [MockBall() for _ in range(4)]
    mode.setup(world, balls)

    assert balls[0].team == "Red"
    assert balls[1].team == "Red"
    assert balls[2].team == "Blue"
    assert balls[3].team == "Blue"

def test_dodgeball_tick():
    mode = gm.DodgeballMode()
    class MockWorld:
        pass
    world = MockWorld()
    world.arena = type('Arena', (), {'width': 1000, 'height': 1000})()
    world.dead_balls = []

    class MockBall:
        def __init__(self, team):
            self.x = 0
            self.y = 500
            self.vx = 100
            self.vy = 0
            self.team = team
            self.alive = True
            self.ball_type = "normal"
            self.radius = 10
            self.id = id(self)

    b1 = MockBall("Red")
    b1.x = 495
    b1.vx = 100 # Moving towards right (Blue side)

    b2 = MockBall("Blue")
    b2.x = 505
    b2.vx = -100 # Moving towards left (Red side)

    mode.tick(world, [b1, b2], 0.1)

    # Check if they are pushed back
    assert b1.x <= 490 # 500 - 10
    assert b2.x >= 510 # 500 + 10

def test_dodgeball_check_winner():
    mode = gm.DodgeballMode()
    class MockWorld: pass
    world = MockWorld()
    class MockBall:
        def __init__(self, team, alive=True):
            self.team = team
            self.alive = alive
            self.ball_type = "normal"

    balls = [MockBall("Red", True), MockBall("Blue", False)]
    assert mode.check_winner(world, balls) == "Red"
