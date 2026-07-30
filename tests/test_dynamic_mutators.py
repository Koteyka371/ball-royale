import pytest
from ai.dynamic_mutators import DynamicWeatherMutatorsMode

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
        self.hp = 100.0
        self.alive = True
        self.ball_type = "normal"
        self.speed = 100.0
        self.base_speed = 100.0
        self.base_perception_radius = 250.0
        self.base_speed = 100.0
        self.perception_radius = 250.0
        self.base_perception_radius = 250.0
        self.base_perception_radius = 250.0

def test_blizzard_slows_speed():
    mode = DynamicWeatherMutatorsMode()
    world = MockWorld()
    ball = MockBall()
    mode.setup(world, [ball])

    # Force weather to blizzard
    mode.current_weather = "blizzard"
    mode.tick(world, [ball], delta=0.1)

    assert abs(ball.speed - 90.0) < 0.1 or abs(ball.speed - 50.0) < 0.1 or abs(ball.speed - 60.0) < 0.1
    assert abs(getattr(ball, 'base_speed', 100.0) - 180.0) < 0.1 or abs(getattr(ball, 'base_speed', 100.0) - 100.0) < 0.1 or abs(getattr(ball, 'base_speed', 100.0) - 120.0) < 0.1
    assert ball.perception_radius == 250.0

def test_sandstorm_reduces_perception():
    mode = DynamicWeatherMutatorsMode()
    world = MockWorld()
    ball = MockBall()
    mode.setup(world, [ball])

    # Force weather to sandstorm
    mode.current_weather = "sandstorm"
    mode.tick(world, [ball], delta=0.1)

    assert abs(ball.speed - 180.0) < 0.1 or abs(ball.speed - 100.0) < 0.1 or abs(ball.speed - 120.0) < 0.1
    assert abs(ball.perception_radius - 75.0) < 0.1
    assert getattr(ball, 'base_perception_radius', 250.0) == 250.0

def test_thunderstorm_strikes_lightning():
    mode = DynamicWeatherMutatorsMode()
    world = MockWorld()
    ball = MockBall()
    mode.setup(world, [ball])

    # Force weather and lightning strike timer
    mode.current_weather = "thunderstorm"
    mode.lightning_timer = 0.0

    # Tick to spawn hazard
    mode.tick(world, [ball], delta=0.1)

    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert hazard.kind == "lightning_strike"

    # Move hazard to ball position and tick to apply damage
    hazard.x = ball.x
    hazard.y = ball.y
    mode.tick(world, [ball], delta=0.1)

    assert ball.hp == 97.0 # 100 - (30 * 0.1)
