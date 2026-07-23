import pytest

class MockBall:
    def __init__(self, traits=None):
        self.traits = traits or []
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

def test_day_night_traits():
    from ai.game_modes import DayNightMode
    mode = DayNightMode()
    world = MockWorld()

    light_ball = MockBall(["light"])
    shadow_ball = MockBall(["shadow"])

    # Test Day
    world.arena.is_night = False
    mode.apply_dynamic_traits(world, [light_ball, shadow_ball], 0.1)

    assert light_ball.speed > 100.0
    assert light_ball.perception_radius > 150.0

    assert shadow_ball.stealth == False
    assert shadow_ball.crit_chance == 0.1

    # Test Night
    world.arena.is_night = True
    mode.apply_dynamic_traits(world, [light_ball, shadow_ball], 0.1)

    assert light_ball.speed == 100.0
    assert light_ball.perception_radius == 150.0

    assert shadow_ball.stealth == True
    assert shadow_ball.crit_chance > 0.1
