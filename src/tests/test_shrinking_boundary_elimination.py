import pytest
from ai.game_modes import ShrinkingSafeZoneMode
import math

class MockBall:
    def __init__(self, x=0, y=0, radius=10):
        self.id = 1
        self.x = x
        self.y = y
        self.radius = radius
        self.hp = 1000.0
        self.alive = True
        self.ball_type = "base"
        self.team = "base"

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

def test_shrinking_safe_zone_mode():
    mode = ShrinkingSafeZoneMode()
    world = MockWorld()
    ball_in = MockBall(500, 500)
    ball_out = MockBall(1500, 1500)
    ball_out.team = "enemy"
    ball_out.ball_type = "enemy"
    balls = [ball_in, ball_out]

    mode.setup(world, balls)

    assert mode.zone_radius == 1000.0

    # Shrink a bit
    mode.tick(world, balls, delta=10.0)

    assert mode.zone_radius == 1000.0 - 15.0 * 10.0

    # Inside ball should not take damage
    assert ball_in.hp == 1000.0

    # Outside ball should take damage
    assert ball_out.hp < 1000.0

    # Check winning condition
    assert mode.check_winner(world, balls) is None

    ball_out.alive = False

    assert mode.check_winner(world, balls) == "base"
