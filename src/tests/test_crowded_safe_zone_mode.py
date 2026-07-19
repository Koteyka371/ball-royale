import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self, width=1000, height=1000):
        self.width = width
        self.height = height

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []

class MockBall:
    def __init__(self, id, x, y, alive=True, ball_type="normal"):
        self.id = id
        self.x = x
        self.y = y
        self.alive = alive
        self.ball_type = ball_type

def test_crowded_safe_zone_registered():
    assert "crowded_safe_zone" in GAME_MODES
    mode = GAME_MODES["crowded_safe_zone"]
    assert mode.name == "Crowded Safe Zone"

def test_crowded_safe_zone_shrink_rate_adjustment():
    mode = GAME_MODES["crowded_safe_zone"]

    # Initialize some mock data
    world = MockWorld()

    mode.setup(world, [])

    # Place safe zone at 500, 500 with radius 200
    mode.zone_x = 500.0
    mode.zone_y = 500.0
    mode.zone_radius = 200.0
    mode.base_shrink_rate = 10.0

    # Test 1: No players outside
    # All players inside the safe zone
    balls_inside = [
        MockBall(1, 500.0, 500.0),
        MockBall(2, 550.0, 550.0),
    ]

    mode.apply_dynamic_traits(world, balls_inside, 1.0)
    # 0 players outside, shrink_rate = 10.0 * (1.0 + 0 * 0.5) = 10.0
    assert mode.shrink_rate == 10.0

    # Test 2: Two players outside
    balls_mixed = [
        MockBall(1, 500.0, 500.0), # Inside
        MockBall(2, 900.0, 900.0), # Outside
        MockBall(3, 100.0, 100.0), # Outside
    ]

    mode.apply_dynamic_traits(world, balls_mixed, 1.0)
    # 2 players outside, shrink_rate = 10.0 * (1.0 + 2 * 0.5) = 20.0
    assert mode.shrink_rate == 20.0

    # Test 3: Ignores spectators and dead balls
    balls_with_spectators = [
        MockBall(1, 900.0, 900.0), # Outside, alive
        MockBall(2, 900.0, 900.0, ball_type="spectator"), # Outside, spectator
        MockBall(3, 900.0, 900.0, alive=False), # Outside, dead
    ]

    mode.apply_dynamic_traits(world, balls_with_spectators, 1.0)
    # Only 1 valid player outside, shrink_rate = 10.0 * (1.0 + 1 * 0.5) = 15.0
    assert mode.shrink_rate == 15.0
