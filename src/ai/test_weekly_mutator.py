from game_modes import GameMode
from unittest.mock import MagicMock
import time

class MockWorld:
    pass

class MockBall:
    def __init__(self, ball_type="brawler"):
        self.ball_type = ball_type
        self.base_damage = 10.0
        self.damage = 10.0
        self.base_speed = 100.0
        self.speed = 100.0
        self.lifesteal = 0.0
        self.mass = 1.0

def test_weekly_mutator():
    mode = GameMode()
    world = MockWorld()

    # We mock time.time() to test different weeks
    original_time = time.time

    try:
        # Week 0 - low_gravity
        time.time = lambda: 0 * 7 * 24 * 3600
        ball = MockBall()
        mode.setup(world, [ball])
        assert world.weekly_mutator == "low_gravity"
        assert ball.mass == 0.5

        # Week 1 - double_damage
        time.time = lambda: 1 * 7 * 24 * 3600
        ball = MockBall()
        mode.setup(world, [ball])
        assert world.weekly_mutator == "double_damage"
        # damage has 0.9 * 2 = 1.8 from modifiers, season 1 = global_speed so damage 10 -> 20
        assert ball.base_damage == 20.0

        # Week 2 - high_speed
        time.time = lambda: 2 * 7 * 24 * 3600
        ball = MockBall()
        mode.setup(world, [ball])
        assert world.weekly_mutator == "high_speed"

        # Week 3 - vampirism
        time.time = lambda: 3 * 7 * 24 * 3600
        ball = MockBall()
        mode.setup(world, [ball])
        assert world.weekly_mutator == "vampirism"
        assert ball.lifesteal == 0.5

    finally:
        time.time = original_time
