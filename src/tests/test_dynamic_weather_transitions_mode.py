import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.weather = "clear"

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, name, data):
        self.events.append((name, data))

class MockBall:
    def __init__(self):
        self.alive = True
        self.speed = 100.0
        self.base_speed = 100.0

def test_dynamic_weather_transitions_setup():
    mode = GAME_MODES["dynamic_weather_transitions"]
    world = MockWorld()
    balls = [MockBall(), MockBall()]

    mode.setup(world, balls)

    assert mode.current_stage == 0
    assert mode.weather == "clear"
    assert mode.weather_timer == 20.0
    assert world.arena.weather == "clear"

def test_dynamic_weather_transitions_tick():
    mode = GAME_MODES["dynamic_weather_transitions"]
    world = MockWorld()
    balls = [MockBall()]

    mode.setup(world, balls)

    # Tick past the first stage (20.0 seconds)
    mode.tick(world, balls, delta=20.0)

    assert mode.current_stage == 1
    assert mode.weather == "cloudy"
    assert mode.weather_timer == 20.0
    assert world.arena.weather == "cloudy"
    assert any(e[0] == "weather_transition" and e[1]["new_weather"] == "cloudy" for e in world.events)

    # Tick past the next stage
    mode.tick(world, balls, delta=20.0)

    assert mode.current_stage == 2
    assert mode.weather == "storm"

    # Tick past the final stage
    mode.tick(world, balls, delta=20.0)

    assert mode.current_stage == 3
    assert mode.weather == "blizzard"

    # Tick again, should stay at blizzard
    mode.tick(world, balls, delta=20.0)
    assert mode.current_stage == 3
    assert mode.weather == "blizzard"
    assert mode.weather_timer == 9999.0

def test_dynamic_weather_transitions_apply_traits():
    mode = GAME_MODES["dynamic_weather_transitions"]
    world = MockWorld()
    ball = MockBall()
    balls = [ball]

    mode.setup(world, balls)
    mode.weather = "storm"


    # Reset ball's ball_type and traits to avoid inheriting Base GameMode modifiers
    ball.ball_type = "unknown"
    ball.traits = []

    # Base mode gets called in GameMode (which dynamic mode doesn't explicitly call super() inside apply_dynamic_traits but the test environment might if we did), actually wait, does Base call it?

    mode.apply_dynamic_traits(world, balls, delta=1.0)


    expected_storm = getattr(ball, "base_speed", 100.0) * 0.8
    assert abs(ball.speed - expected_storm) < 0.1


    mode.weather = "blizzard"

    # Reset ball's ball_type and traits to avoid inheriting Base GameMode modifiers
    ball.ball_type = "unknown"
    ball.traits = []

    # Base mode gets called in GameMode (which dynamic mode doesn't explicitly call super() inside apply_dynamic_traits but the test environment might if we did), actually wait, does Base call it?

    mode.apply_dynamic_traits(world, balls, delta=1.0)


    expected_blizzard = getattr(ball, "base_speed", 100.0) * 0.5
    assert abs(ball.speed - expected_blizzard) < 0.1


    mode.weather = "clear"

    # Reset ball's ball_type and traits to avoid inheriting Base GameMode modifiers
    ball.ball_type = "unknown"
    ball.traits = []

    # Base mode gets called in GameMode (which dynamic mode doesn't explicitly call super() inside apply_dynamic_traits but the test environment might if we did), actually wait, does Base call it?

    mode.apply_dynamic_traits(world, balls, delta=1.0)


    expected_clear = getattr(ball, "base_speed", 100.0)
    assert abs(ball.speed - expected_clear) < 0.1
