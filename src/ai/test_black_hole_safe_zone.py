import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.ai.game_modes import BlackHoleSafeZoneMode

class MockBall:
    def __init__(self, ball_type="player", x=0, y=0, hp=100, team=None):
        self.ball_type = ball_type
        self.x = x
        self.y = y
        self.hp = hp
        self.alive = True
        self.team = team or ball_type

class MockWorld:
    def __init__(self, w=1000, h=1000):
        class MockArena:
            def __init__(self, w, h):
                self.width = w
                self.height = h
        self.arena = MockArena(w, h)

def test_black_hole_safe_zone_mode():
    mode = BlackHoleSafeZoneMode()
    world = MockWorld()

    # Place a ball in the safe zone
    b1 = MockBall(x=500, y=500)

    # Place a ball way outside the safe zone
    b2 = MockBall(x=1500, y=1500)

    mode.tick(world, [b1, b2], delta=1.0)

    # B1 should be pulled toward center

    # B2 should take outside damage
    assert b2.hp < 100
