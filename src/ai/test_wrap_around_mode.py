import pytest
from unittest.mock import MagicMock
from ai.game_modes import WrapAroundMode

class MockArena:
    def __init__(self):
        self.width = 800.0
        self.height = 600.0
        self.name = "Test Arena"

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, payload):
        self.events.append((event_type, payload))

class MockBall:
    def __init__(self, x, y, vx, vy, alive=True):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.alive = alive
        self.radius = 15.0
        self.id = "test_ball"
        self.internal_temperature = 20.0
        self.cooling_booster_timer = 0.0
        self.warming_booster_timer = 0.0

        self.ball_type = "easy"
        self.max_stamina = 100.0
        self.stamina = 100.0
        self.base_speed = 200.0
        self.speed = 200.0
        self.base_damage = 10.0
        self.original_base_damage = 10.0
        self.traits = []
        self.weather_immunity_timer = 0.0
        self.in_mirror_dimension = False
        self.intangible = False
        self.vision_radius = 300.0
        self.invisible = False
        self.speed_multiplier = 1.0

def test_wrap_around_mode_tick_left_boundary():
    mode = WrapAroundMode()
    world = MockWorld()

    # Ball past left boundary (x - radius <= 0)
    # x = 10, radius = 15 -> x - radius = -5
    ball = MockBall(x=10.0, y=300.0, vx=-100.0, vy=50.0)
    balls = [ball]

    mode.tick(world, balls, 0.016)

    # Check if teleported to right side (arena_width - radius - 1.0)
    # 800 - 15 - 1 = 784
    assert ball.x == 784.0
    # Check if velocity inverted
    assert ball.vx == 100.0
    # Y and Vy should remain unchanged
    assert ball.y == 300.0
    assert ball.vy == 50.0

def test_wrap_around_mode_tick_right_boundary():
    mode = WrapAroundMode()
    world = MockWorld()

    # Ball past right boundary (x + radius >= 800)
    # x = 790, radius = 15 -> x + radius = 805
    ball = MockBall(x=790.0, y=300.0, vx=100.0, vy=50.0)
    balls = [ball]

    mode.tick(world, balls, 0.016)

    # Check if teleported to left side (radius + 1.0)
    # 15 + 1 = 16
    assert ball.x == 16.0
    # Check if velocity inverted
    assert ball.vx == -100.0

def test_wrap_around_mode_tick_top_boundary():
    mode = WrapAroundMode()
    world = MockWorld()

    # Ball past top boundary (y - radius <= 0)
    # y = 10, radius = 15 -> y - radius = -5
    ball = MockBall(x=400.0, y=10.0, vx=50.0, vy=-100.0)
    balls = [ball]

    mode.tick(world, balls, 0.016)

    # Check if teleported to bottom side (arena_height - radius - 1.0)
    # 600 - 15 - 1 = 584
    assert ball.y == 584.0
    # Check if velocity inverted
    assert ball.vy == 100.0

def test_wrap_around_mode_tick_bottom_boundary():
    mode = WrapAroundMode()
    world = MockWorld()

    # Ball past bottom boundary (y + radius >= 600)
    # y = 590, radius = 15 -> y + radius = 605
    ball = MockBall(x=400.0, y=590.0, vx=50.0, vy=100.0)
    balls = [ball]

    mode.tick(world, balls, 0.016)

    # Check if teleported to top side (radius + 1.0)
    # 15 + 1 = 16
    assert ball.y == 16.0
    # Check if velocity inverted
    assert ball.vy == -100.0

def test_wrap_around_mode_tick_in_bounds():
    mode = WrapAroundMode()
    world = MockWorld()

    # Ball well within bounds
    ball = MockBall(x=400.0, y=300.0, vx=50.0, vy=50.0)
    balls = [ball]

    mode.tick(world, balls, 0.016)

    # Position and velocity should remain unchanged
    assert ball.x == 400.0
    assert ball.y == 300.0
    assert ball.vx == 50.0
    assert ball.vy == 50.0
