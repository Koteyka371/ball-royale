import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.ball_type = "player"
        self.team = "team1"
        self.hp = 100
        self.freeze_timer = 0.0
        self.weather_immunity_timer = 0.0

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []

def test_freezing_edges_royale_mode():
    mode = GAME_MODES.get('freezing_edges_royale')
    assert mode is not None

    world = MockWorld()
    b_safe = MockBall(500, 500)
    b_danger = MockBall(0, 0)
    balls = [b_safe, b_danger]

    mode.setup(world, balls)
    assert mode.safe_radius == 1000.0

    # Tick loop to simulate shrink and freezing
    for _ in range(100):
        mode.tick(world, balls, delta=1.0)

    assert b_safe.hp == 100
    assert b_safe.freeze_timer == 0.0
    assert b_safe.alive is True

    assert b_danger.hp < 100
    assert b_danger.freeze_timer > 5.0
    assert b_danger.alive is False
    assert b_danger.killer == "ice"
