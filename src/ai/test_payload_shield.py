import math
import os
import tempfile
import pytest

from ai.game_modes import EscortMode

class MockWorld:
    pass

class MockBall:
    def __init__(self, x=0, y=0, team=""):
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.ball_type = "player"

def test_payload_shield_cap():
    mode = EscortMode()
    world = MockWorld()

    # We create a payload and some defenders
    mode.payload = MockBall(x=500, y=500, team="Defenders")
    mode.payload.hp = 5000.0
    mode.payload.max_hp = 5000.0

    b1 = MockBall(x=500, y=500, team="Defenders")
    b1.hp = 100.0
    b1.max_hp = 100.0
    b1.shield = 95.0
    b1.max_shield = 100.0

    balls = [mode.payload, b1]

    # One second passes
    mode.tick(world, balls, 1.0)

    # Shield should cap at max_shield (100.0) instead of going to 110.0
    assert b1.shield == 100.0, f"Expected 100.0, got {b1.shield}"

if __name__ == "__main__":
    test_payload_shield_cap()
    print("Test passed!")
