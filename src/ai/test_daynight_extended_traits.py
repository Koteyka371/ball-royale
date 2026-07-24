import pytest

class MockBall:
    def __init__(self, traits=None, ball_type=""):
        self.traits = traits or []
        self.ball_type = ball_type
        self.alive = True
        self.base_speed = 100.0
        self.speed = 100.0
        self.base_perception_radius = 150.0
        self.perception_radius = 150.0
        self.base_crit_chance = 0.1
        self.crit_chance = 0.1
        self.stealth = False

class MockArena:
    def __init__(self):
        self.is_night = False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

def test_day_night_extended_traits():
    from ai.game_modes import DayNightMode
    mode = DayNightMode()
    world = MockWorld()

    vampire_ball = MockBall(["vampire"])
    solar_ball = MockBall(["solar"])
    radiant_ball = MockBall([], "radiant_knight")
    stealth_ball = MockBall([], "stealth_bot")

    # Test Day
    world.arena.is_night = False
    mode.apply_dynamic_traits(world, [vampire_ball, solar_ball, radiant_ball, stealth_ball], 0.1)

    assert solar_ball.speed > 100.0
    assert radiant_ball.speed > 100.0
    assert vampire_ball.stealth == False
    assert stealth_ball.stealth == False

    # Test Night
    world.arena.is_night = True
    mode.apply_dynamic_traits(world, [vampire_ball, solar_ball, radiant_ball, stealth_ball], 0.1)

    assert solar_ball.speed == 100.0
    assert radiant_ball.speed == 100.0
    assert vampire_ball.stealth == True
    assert stealth_ball.stealth == True
