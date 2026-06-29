import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from ai.game_modes import MovingSafeZoneMode

class MockBall:
    def __init__(self, id, ball_type="warrior", alive=True):
        self.id = id
        self.ball_type = ball_type
        self.alive = alive
        self.team = ball_type
        self.hp = 100
        self.x = 500
        self.y = 500

class MockWorld:
    def __init__(self):
        self.arena = type("Arena", (), {"width": 1000, "height": 1000})()

def test_moving_safe_zone_mode():
    mode = MovingSafeZoneMode()
    world = MockWorld()
    balls = [MockBall(1), MockBall(2, "scout")]

    # Place one ball inside, one outside
    balls[0].x = 500
    balls[0].y = 500

    # Radius is 500, so 1100 is way outside
    balls[1].x = 1100
    balls[1].y = 1100

    mode.setup(world, balls)

    assert mode.zone_radius == 500.0

    # Tick should deal damage to ball outside
    mode.tick(world, balls, delta=1.0)

    assert mode.zone_radius == 490.0
    assert balls[0].hp == 100
    assert balls[1].hp == 90

    # Tick for another 10 seconds to kill the outside ball
    mode.tick(world, balls, delta=10.0)

    assert balls[0].hp == 100
    assert balls[1].hp == 0
    assert not balls[1].alive

    assert mode.check_winner(world, balls) == "warrior"
