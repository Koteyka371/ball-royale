import math
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.ball_type = "normal"
        self.vx = 0.0
        self.vy = 0.0
        self.weather_immunity_timer = 0.0

def test_black_hole_weather_mode_exists():
    assert 'black_hole_weather' in GAME_MODES
    mode = GAME_MODES['black_hole_weather']
    assert mode.name == "Black Hole Weather"
    assert mode.weather == "black_hole_storm"

def test_black_hole_weather_pulls_balls():
    mode = GAME_MODES['black_hole_weather']
    world = MockWorld()
    b = MockBall(100, 500) # Left of center (500, 500)

    old_x = b.x
    mode.tick(world, [b], delta=1.0)

    assert b.x > old_x, "Ball should be pulled right towards center"
    assert b.vx > 0.0, "Ball velocity should increase towards center"

def test_black_hole_weather_immunity():
    mode = GAME_MODES['black_hole_weather']
    world = MockWorld()
    b = MockBall(100, 500)
    b.weather_immunity_timer = 5.0

    old_x = b.x
    mode.tick(world, [b], delta=1.0)

    assert b.x == old_x, "Immune ball should not be pulled"
    assert b.vx == 0.0, "Immune ball should not gain velocity"
