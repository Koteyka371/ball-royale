import pytest
from ai.game_modes import CentralMassiveGravityWellMode, GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []

class MockBall:
    def __init__(self, x, y, team="red"):
        self.x = x
        self.y = y
        self.alive = True
        self.team = team
        self.ball_type = "normal"
        self.hp = 100.0

def test_central_mgw():
    mode = CentralMassiveGravityWellMode()
    assert "central_massive_gravity_well" in GAME_MODES
    world = MockWorld()
    # placed at (500, 500) so it's in the center and will take damage
    b1 = MockBall(500.0, 500.0)
    # placed far away so it just gets pulled
    b2 = MockBall(900.0, 900.0, team="blue")

    balls = [b1, b2]
    mode.setup(world, balls)

    # Tick once
    mode.tick(world, balls, 0.016)

    # B1 should take damage, b2 should be pulled
    assert b1.hp < 100.0
    assert b2.x < 900.0
    assert b2.y < 900.0

    # Winner shouldn't exist since both are alive
    assert mode.check_winner(world, balls) is None
