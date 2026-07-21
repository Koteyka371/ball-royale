import pytest

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

from ai.ball_brain import BallBrain

def test_snow_tires_buff():
    world = MockWorld("snow")
    ball = MockBall("snow_tires")

    brain = BallBrain(ball, world)
    brain.process(0.016) # applies skin buffs

    assert ball.speed == 125.0
    assert ball.status_resistance == 0.30

def test_snow_tires_no_buff_in_clear_weather():
    world = MockWorld("clear")
    ball = MockBall("snow_tires")

    brain = BallBrain(ball, world)
    brain.process(0.016)

    assert ball.speed == 100.0
    assert ball.status_resistance == 0.0

def test_other_skins_no_buff_in_snow():
    world = MockWorld("snow")
    ball = MockBall("default")

    brain = BallBrain(ball, world)
    brain.process(0.016)

    assert ball.speed == 100.0
    assert ball.status_resistance == 0.0
