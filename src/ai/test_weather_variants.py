import pytest
from ai.ball_brain import BallBrain

class MockArena:
    def __init__(self, weather="clear"):
        self.weather = weather
        self.width = 1000
        self.height = 1000

class MockGameMode:
    def __init__(self, weather="clear"):
        self.weather = weather
        self.name = "Test Mode"

class MockWorld:
    def __init__(self, weather="clear"):
        self.arena = MockArena(weather)
        self.game_mode = MockGameMode(weather)

class MockBall:
    def __init__(self, skin="default"):
        self.skin = skin
        self.x = 0
        self.y = 0
        self.hp = 100
        self.max_hp = 100
        self.speed = 100.0
        self.status_resistance = 0.0


def test_raincoat_buff_in_rain():
    world = MockWorld("heavy_rain")
    ball = MockBall("raincoat")

    brain = BallBrain(ball, world)
    brain.process(0.016)

    assert ball.speed == 125.0
    assert ball.status_resistance == 0.30

def test_raincoat_no_buff_in_clear_weather():
    world = MockWorld("clear")
    ball = MockBall("raincoat")

    brain = BallBrain(ball, world)
    brain.process(0.016)

    assert ball.speed == 100.0
    assert ball.status_resistance == 0.0

def test_sand_tires_buff_in_sandstorm():
    world = MockWorld("sandstorm")
    ball = MockBall("sand_tires")

    brain = BallBrain(ball, world)
    brain.process(0.016)

    assert ball.speed == 125.0
    assert ball.status_resistance == 0.30

def test_sand_tires_no_buff_in_clear_weather():
    world = MockWorld("clear")
    ball = MockBall("sand_tires")

    brain = BallBrain(ball, world)
    brain.process(0.016)

    assert ball.speed == 100.0
    assert ball.status_resistance == 0.0

def test_lightning_rod_buff_in_thunderstorm():
    world = MockWorld("thunderstorm")
    ball = MockBall("lightning_rod")

    brain = BallBrain(ball, world)
    brain.process(0.016)

    assert ball.speed == 125.0
    assert ball.status_resistance == 0.30

def test_lightning_rod_no_buff_in_clear_weather():
    world = MockWorld("clear")
    ball = MockBall("lightning_rod")

    brain = BallBrain(ball, world)
    brain.process(0.016)

    assert ball.speed == 100.0
    assert ball.status_resistance == 0.0
